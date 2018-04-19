# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:58:50 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import time

import EmbeddedCom
import RfidCommandAnalysis

from redisqueue import RedisQueue
import redis

import socket
import json

import threading
#import Com4GModularClass

sysdict = {'ts': 1, 'ss': 30, 'a1': 1, 'a2': 0, 'a3': 0, 'a4': 0, 'aw': 3000, 'sip1': '58.214.232.163', 'sip2': '',
           'sip3': '', 'sip4': ''}
pool = None
redisconnpool = None
usedAnt = 1
usedPower = 1024
EPCProsseRedisflg = 0
GetTagProsseFlg = 0

epcsendthreadalive = 0

isusesubcommand = 1
issysset = 0
rfidcallbackdata = b''
devID = b''
rfidcallbackProssdata = b''
RfidCMD = RfidCommandAnalysis.RfidCMDAnalysis()


def WriteToJsonFile(fpath, fdict):
    try:
        with open(fpath, 'w') as f:
            json.dump(fdict, f)
            return 'OK'
    except:
        return None


def ReadFromJsonFile(fpath):
    try:
        with open(fpath, 'r') as f:
            data = json.load(f)
            print(data)
        return data
    except:
        return None


def SysIniJson():
    global sysdict
    dictt = ReadFromJsonFile('Rfidsys.json')
    if dictt != None:
        sysdict = dictt
        print(sysdict)
    else:
        WriteToJsonFile('Rfidsys.json', sysdict)
    print(sysdict['sip1'])

    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=0)
        conn.mset(sysdict)
        print(sysdict)
    except:
        return False
    return True


def RfidCallbackprossData(data):
    global rfidcallbackProssdata
    global RfidCMD
    global e
    tempdata = b''
    tempuseddata = b''
    s = -1
    end = 0
    if len(rfidcallbackProssdata) == 0:
        rfidcallbackProssdata = data
    else:
        rfidcallbackProssdata += data
    #    print ('rfidcallbackProssdata start:{0}'.format(rfidcallbackProssdata))
    while True:
        if end == -1:
            break

        s = rfidcallbackProssdata.find(b'\xff', end)
        if s == -1:
            return
        end = rfidcallbackProssdata.find(b'\xff', s + 1)
        if end == -1:
            tempdata = rfidcallbackProssdata[s:]
        else:
            tempdata = rfidcallbackProssdata[s:end]
        tempuseddata += tempdata
        ret = RfidCMD.ProcessorData(tempdata)
        #        print('ProcessorData DevID{0}'.format(devID))
        #        print('Pro ok:{0},{1}'.format(ret[0], ret[1]))
        # logger.debug('RfidCallbackprossData:{0},{1}'.format(ret[0], ret[1]))
        if ret[0] > 0:
            ProssAll(ret[1])
            # tempnotusedata=rfidcallbackProssdata[len(tempdata):]
            #            rfidcallbackProssdata=tempnotusedata
            continue
        else:
            while end != -1:
                end = rfidcallbackProssdata.find(b'\xff', end + 1)
                if end == -1:
                    tempdata = rfidcallbackProssdata[s:]
                else:
                    tempdata = rfidcallbackProssdata[s:end]
                tempuseddata += tempdata
                ret = RfidCMD.ProcessorData(tempdata)
                #                print('ProcessorData DevID{0}'.format(devID))
                #                print('Pro ok in while:{0},{1}'.format(ret[0], ret[1]))
                # logger.debug('RfidCallbackprossData--:{0},{1}'.format(ret[0], ret[1]))
                if ret[0] > 0:
                    ProssAll(ret[1])
                    # tempnotusedata=rfidcallbackProssdata[len(tempdata):]
                    break
                else:
                    pass

    rfidcallbackProssdata = rfidcallbackProssdata[len(tempuseddata):]



edataqueueformat = 0


def EPCSendToServerThread():
    # global redisconnpool
    s_conn = None
    usedkey = ''

    try:
        s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if s_conn.ping():
            print('EPCSendToServerThread ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThread err')
        s_conn = None
        return False

    while epcsendthreadalive:
        # InsertToPostgresql(devID,epc)
        if s_conn == None:
            try:
                s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
                if s_conn.ping():
                    print('EPCSendToServerThread ok')
                else:
                    print('shawanyi')
                s_conn = None
                time.sleep(1)
                continue
            except:  #
                print('EPCSendToServerThread err')
                s_conn = None
                time.sleep(1)
                continue
        else:
            if usedkey == '':
                usedkey = s_conn.lpop('EPCDatasqueuekey')
                if usedkey == None:
                    time.sleep(2)
                    continue
            if s_conn.exists(usedkey):
                try:
                    epc = s_conn.zrange(usedkey, 0, -1)
                    print('to postgresql')
                    print(epc)
                    for var in epc:
                        sdevs = b'DEVID:' + devID + b';' + var + b';'
                        print(sdevs)
#                        state = rt4g.Senddatasfornet(sdevs)
#                        print(state)
                        time.sleep(1)
                    s_conn.delete(usedkey)
                    usedkey = ''
                    time.sleep(1)
                except:
                    time.sleep(1)
                    continue
            else:
                usedkey = ''
                continue
        time.sleep(2)


def EPCToSqueue(pool=None, keyname='EPCDatasqueuekey'):
    global edataqueueformat
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if conn.ping():
            print('conn ok')
        else:
            print('shawanyi')
    except:  #
        return False

    usdnewkeyname = 'devIDEPC-%d' % (edataqueueformat)
    print('EPCToSqueue:' + usdnewkeyname)
    edataqueueformat = (edataqueueformat + 1) % 10
    #    if conn==None:
    #        conn = redisconnpool
    if conn.exists('devIDEPC'):

        if conn.exists(usdnewkeyname):
            conn.delete(usdnewkeyname)

        try:
            pipe = conn.pipeline()
            # pipe.watch(usedkey)
            pipe.multi()
            pipe.rename('devIDEPC', usdnewkeyname)
            pipe.expire(usdnewkeyname, 1800)
            pipe.rpush(keyname, usdnewkeyname)
            pipe.execute()
        except:
            print('pipe EPCToSqueue err')
            return False
        return True
    else:
        return False


def EPCProsseRedis1():
    global EPCProsseRedisflg
    EPCProsseRedisflg += 1
    if EPCProsseRedisflg > int(sysdict['ss']):  # int(sysdict['ts']):  # 30:
        EPCProsseRedisflg = 0
        return (EPCToSqueue(pool=redisconnpool, keyname='EPCDatasqueuekey'))




def comrecvcallbackpross(data):
    global RfidCMD
    global e

    # logger.debug('comrecvcallbackpross data:{0}'.format(data))
    RfidCallbackprossData(data)
    return




e = EmbeddedCom.ComCOMThread(Port='/dev/ttyAMA3', baudrate=115200, timeout=0.1, RCallarg=rfidcallbackdata,
                             ReceiveCallBack=comrecvcallbackpross)
#e = EmbeddedCom.ComCOMThread(Port='/dev/ttyAMA3', baudrate=115200, timeout=0.1, RCallarg=None,
#                             ReceiveCallBack=None)
tag22rev = 0
tag29rev = 0


def ProssCommand(data):
    global issysset
    global devID
#    global e
    global tag22rev
    global tag29rev
    sendcmd = b''
    if len(data) < 2:
        return False
    cm, cmvalue = data[0].split(b':')
    if b'Command' != cm:
        return False
    status, stvalue = data[1].split(b':')
    if b'Status' != status:
        return False
    if b'0000' != stvalue:
        return False

    if b'0C' == cmvalue:
        if issysset < 5:
            if len(data) >= 3:
                sys, value = data[2].split(b':')
                if b'SYS' != sys:
                    return False
                if b'BOOTLOADER' == value:  #
                    issysset = 1
                    return True
                elif b'APP' == value:
                    issysset = 2
                    return True
                else:
                    return False

            else:
                return False
    elif b'09' == cmvalue:
        issysset = 1
        return True
    elif b'04' == cmvalue:
        # issysset=2
        issysset = 10
        return True
    elif b'10' == cmvalue:
        if len(data) >= 3:
            sn, value = data[2].split(b':')
            if b'SN' == sn:
                devID = value
                if isusesubcommand == 0:
                    issysset = 6
                else:
                    issysset = 8
                return True
            else:
                return False
        else:
            return False
    elif b'22' == cmvalue:
        if len(data) >= 3:
            nums, value = data[2].split(b':')
            if b'NUMS' == nums:
                tag22rev = int(value, base=16)
                tag29rev = 0
                print('22recvnum:{0},{1}'.format(tag22rev, tag29rev))
                # logger.debug('ProssCommand 22recvnum:{0},{1}'.format(tag22rev,tag29rev))
            else:
                pass
        #        print(data)
        issysset = 7
        return True
    elif b'29' == cmvalue:
        if len(data) >= 3:
            nums, value = data[2].split(b':')
            if b'NUMS' == nums:
                getnums = int(value, base=16)
                tag29rev += getnums  # int(value,base=16)
                print('29recvnum:{0},{1}'.format(tag22rev, tag29rev))
                # logger.debug('ProssCommand 29recvnum:{0},{1}'.format(tag22rev,tag29rev))
                if getnums <= 0:
                    tag22rev = 0
                    tag29rev = 0
                    issysset = 6
                    print('29finish is zero')
                    # logger.debug('ProssCommand 29finish is zero')
                    return True
                else:
                    # print(data)
                    for vdata in data:
                        if b'EPC:' in vdata:
                            # epcdata=devID+b','+vdata
                            if redisconnpool != None:
                                # redisconnpool.zadd('devIDEPC',epcdata,1)
                                redisconnpool.zadd('devIDEPC', vdata, 1)
                                # print('EPC:{0}'.format(vdata))
                    # print(redisconnpool.zrange('devIDEPC',0,-1))

            else:
                pass
        if tag29rev >= tag22rev:
            tag22rev = 0
            tag29rev = 0
            issysset = 6
            print('29finish')
            # logger.debug('ProssCommand 29finish')
        else:
            #            pass
            sendcmd = RfidCMD.GetTagMultipleCommand()
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            # logger.debug('ProssCommand GetTagMultiple:{0},{1}'.format(tag22rev,tag29rev))
            send = e.WriteSerialCOM(sendcmd[1])
        #        print(data)
        return True
    elif b'91' == cmvalue:
        issysset = 2
        return True
    elif b'92' == cmvalue:
        issysset = 2
        return True
    else:
        return False


def ProssAll(data):
    s = -1
    end = -1
    Muldata = b''
    while True:
        s = data.find(b'Command', end + 1)
        if s == -1:
            break
        end = data.find(b'Command', s + 1)
        if end == -1:
            Muldata = data[s:]
        else:
            Muldata = data[s:end]
        td = Muldata.lstrip(b'\r\n')
        td = Muldata.rstrip(b'\r\n')
        t = td.split(b'\r\n')
        ProssCommand(t)
        if end == -1:
            break


def RFIDGetTagStarOrNotSub(flg=0):
    global isusesubcommand
    if flg == 0:
        isusesubcommand = 0
    else:
        isusesubcommand = 1
    RFIDGetTagStart()




def RFIDGetTagStart():
    global issysset
    global e
    global pool
    global redisconnpool
    global GetTagProsseFlg
    global epcsendthreadalive
    sl = 1

    if not SysIniJson():  # if not SysIni():
        print('SysIni Erro')
        return

    sleeptimes = 0
    if e.RunAllStart():
        pass
    else:
        print('RFIDGetTagStart ERR Return')
        return

    pool = redis.ConnectionPool(host='127.0.0.1', password='123456', port=6379, db=1)
    # q = RedisQueue(name='RfidControl',host='127.0.0.1',psw='123456')
    try:
        redisconnpool = redis.Redis(connection_pool=pool)
        if redisconnpool.ping():
            pass
    except:
        e.CloseSerialCOM()
        return

#    epcsendthreadalive = 1
#    thread_sendepc = threading.Thread(target=EPCSendToServerThread, name='EPCSendToServerThread')
#    thread_sendepc.setDaemon(True)
#    thread_sendepc.start()

    while issysset < 200:

        if issysset != 199:
            # EPCProsseRedis()
            EPCProsseRedis1()

        if issysset == 0:
            sendcmd = RfidCMD.IsAppoBootLoad()
            print('IsAppoBootLoad:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 1:
            sendcmd = RfidCMD.BtoApp()
            print('BtoApp:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 2:
            sendcmd = RfidCMD.GetDNum()
            # sendcmd=RfidCMD.ApptoB()
            print('GetDNum:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 6:
            GetTagProsseFlg += 1
            if GetTagProsseFlg < int(sysdict['ts']):
                time.sleep(sl)
                continue
            sendcmd = RfidCMD.GetTagMultiple()
            GetTagProsseFlg = 0
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            sleeptimes = 0
            issysset = 106
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 7:
            sendcmd = RfidCMD.GetTagMultipleCommand()
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            sleeptimes = 0
            issysset = 107
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 106:
            sleeptimes += 1
            if sleeptimes > 10:
                issysset = 6
                loggererro.debug('106Sleep')
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 107:
            sleeptimes += 1
            if sleeptimes > 10:
                issysset = 7
                loggererro.debug('107Sleep')
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 8:
            sendcmd = RfidCMD.SubSetGetTagData()
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 9:
            sendcmd = RfidCMD.SetAntEnable(ant1=int(sysdict['a1']), ant2=int(sysdict['a2']), ant3=int(sysdict['a3']),
                                           ant4=int(sysdict['a4']))
            print('SetAntEnable:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 10:
            sendcmd = RfidCMD.SetAntPower(ant1=int(sysdict['a1']), ant2=int(sysdict['a2']), ant3=int(sysdict['a3']),
                                          ant4=int(sysdict['a4']), rpower=int(sysdict['aw']))
            print('SetAntPower:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        else:
            time.sleep(sl)  # time.sleep(2)




if __name__ == '__main__':
    RFIDGetTagStarOrNotSub(0)  # RFIDGetTagStart()#main()
