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

from PrintLoggerClass import Logger
#from  RedisMessagesHelper import RedisMessagesHelper
from redisqueue import RedisQueue
import redis

#import RFIDSYSSqliteClass

import socket
import json

import threading
#import psycopg2
import datetime

sysdict={'ts':1,'ss':30,'a1':1,'a2':0,'a3':0,'a4':0,'aw':3000,'sip1':'218.240.49.25','sip2':'','sip3':'','sip4':''}

so4gpath="./libEC20.so"
ll4g = ctypes.cdll.LoadLibrary
lib4g = ll4g(so4gpath)
is4grun=0

funec20inirun=lib4g.EC20_init_run
funec20inirun.restype = c_int
funec20shutdown=lib4g.EC20_Shutdown
funec20shutdown.restype = c_int

pool = None
redisconnpool = None
loggererro=Logger(logname='logerro.txt',loglevel=1,logger='RfidReadAndWrite.py').getlog()
logger = Logger(logname='log.txt', loglevel=1, logger="RfidReadAndWrite.py").getlog()
#syskey=b''
#sysstatus=b''
usedAnt=1
usedPower=1024
EPCProsseRedisflg=0
GetTagProsseFlg=0

epcsendthreadalive=0

isusesubcommand=1
issysset=0        
rfidcallbackdata=b''
devID=b''
rfidcallbackProssdata=b''
RfidCMD=RfidCommandAnalysis.RfidCMDAnalysis()
def WriteToJsonFile(fpath,fdict):
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
    dictt=ReadFromJsonFile('Rfidsys.json')
    if dictt != None:
        sysdict=dictt
        print (sysdict)
    else:
        WriteToJsonFile('Rfidsys.json',sysdict)
    print (sysdict['sip1'])
    
    try:
        conn = redis.Redis(host='127.0.0.1',password='123456',port=6379,db=0)
        conn.mset(sysdict)
        print(sysdict)
    except:
        return False
        
    if SysIni4G()<0:
        return False
    return True

def SysIni4G():
    global is4grun
    if is4grun != 0:
        return 0
    print('start to set EC20...')
    ret=funec20inirun()
    if ret < 0:
        is4grun=0
        print('start EC20 Err')
        return ret
    is4grun = 1
    print('end to set EC20')
    return 0
def SysIni4GClose():
    global is4grun
    if is4grun == 0:
        return 0
    print('close to set EC20...')
    ret=funec20shutdown()
    if ret < 0:
        #is4grun=0
        print('close EC20 Err')
        return ret
    is4grun = 0
    print('close to set EC20')
    return 0

#def SysIni():
#    global sysdict
#    rt=RFIDSYSSqliteClass.RfidSysSqlite3Class(db='/opt/Test/Rfidsys.db')
#    dictt=rt.Sqlite3Getdata()
#    if dictt==None:
#        ret=rt.Sqlite3creattabl()
#        if not ret:
#            return False
#        else:
#            dictt=rt.Sqlite3Getdata()
#    sysdict=dictt
#    try:
#        conn=redis.Redis(host='127.0.0.1',password='123456',port=6379,db=0) 
#        conn.mset(sysdict)
#        print(sysdict)
#    except :
#        return False
#    return True
        
def RfidCallbackprossData(data):
    global rfidcallbackProssdata
    global RfidCMD
    global e
    tempdata=b''
    tempuseddata=b''
    s=-1
    end=0
    if len(rfidcallbackProssdata)==0:
        rfidcallbackProssdata=data
    else:
        rfidcallbackProssdata+=data
#    print ('rfidcallbackProssdata start:{0}'.format(rfidcallbackProssdata))
    while True:
        if end==-1:
            break
        
        s=rfidcallbackProssdata.find(b'\xff',end)
        if s==-1:
            return
        end=rfidcallbackProssdata.find(b'\xff',s+1)
        if end==-1:
            tempdata=rfidcallbackProssdata[s:]
        else:
            tempdata=rfidcallbackProssdata[s:end]
        tempuseddata+=tempdata
        ret=RfidCMD.ProcessorData(tempdata)
#        print('ProcessorData DevID{0}'.format(devID))
#        print('Pro ok:{0},{1}'.format(ret[0], ret[1]))
        #logger.debug('RfidCallbackprossData:{0},{1}'.format(ret[0], ret[1]))
        if ret[0]>0:
            ProssAll(ret[1])
            #tempnotusedata=rfidcallbackProssdata[len(tempdata):]
#            rfidcallbackProssdata=tempnotusedata
            continue
        else:
            while end!=-1:
                end=rfidcallbackProssdata.find(b'\xff',end+1)
                if end==-1:
                    tempdata=rfidcallbackProssdata[s:]
                else:
                    tempdata=rfidcallbackProssdata[s:end]
                tempuseddata+=tempdata
                ret=RfidCMD.ProcessorData(tempdata)
#                print('ProcessorData DevID{0}'.format(devID))
#                print('Pro ok in while:{0},{1}'.format(ret[0], ret[1]))
                #logger.debug('RfidCallbackprossData--:{0},{1}'.format(ret[0], ret[1]))
                if ret[0]>0:
                    ProssAll(ret[1])
                    #tempnotusedata=rfidcallbackProssdata[len(tempdata):]
                    break
                else:
                    pass
                
    #tempnotusedata=rfidcallbackProssdata[s:]            
            #tempnotusedata=rfidcallbackProssdata[len(tempdata):]
    #rfidcallbackProssdata=tempnotusedata
    rfidcallbackProssdata=rfidcallbackProssdata[len(tempuseddata):] 
#    print ('tempnotusedata end:{0}'.format(rfidcallbackProssdata))
    #logger.debug('RfidCallbackprossData not to used:{0}'.format(rfidcallbackProssdata))

#def TestInsertToPostgresql():
#    print ('TestInsertToPostgresql')
#    conn=psycopg2.connect(database="materiel",user="pms",password="pms@pg123",host="58.214.232.165",port="5432")
#    cur=conn.cursor()
#    sqlselectstr="INSERT INTO tb_epc_record (device_id,epc,report_time) \
#                 VALUES ('020001070102020100020105','EPC:2016000000082040',NOW()::timestamp)"
#    print(sqlselectstr)
#    cur.execute(sqlselectstr)
#    conn.commit()
#    conn.close()
#    print ('TestInsertToPostgresql OK')

#def InsertToPostgresql(dev_id,epc):
#    devid=dev_id.decode(encoding='utf-8')
#    print(devid)
#    try:
#         conn=psycopg2.connect(database="materiel",user="pms",password="pms@pg123",host="58.214.232.165",port="5432")
#         print('lin postgresql OK')
#         cur= conn.cursor()
#         #sqlselectstr="INSERT INTO tb_epc_record (device_id,epc,report_time) VALUES \ ('020001070102020100020105','EPC:2016000000082040',NOW()::timestamp)"
#         #cur.execute(sqlselectstr)
#         for var in epc:
#             sqlselectstr=("INSERT INTO tb_epc_record (device_id,epc,report_time) VALUES ('{0}','{1}',NOW()::timestamp)").format(devid,var.decode(encoding='utf-8'))
#             print(sqlselectstr)
#             cur.execute(sqlselectstr)
#         conn.commit()
#         conn.close()
         
#    except:
#         pass

edataqueueformat=0
def EPCSendToServerThread():
    global is4grun    #global redisconnpool
    s_conn=None
    usedkey=''
    try:
        s_conn=redis.Redis(host = '127.0.0.1', password = '123456', port = 6379, db = 1)
        if s_conn.ping():
            print('EPCSendToServerThread ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThread err')
        s_conn=None
        return False

    while epcsendthreadalive:
                    #InsertToPostgresql(devID,epc)
        if s_conn==None:
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
            if usedkey=='':
                usedkey=s_conn.lpop('EPCDatasqueuekey')
                if usedkey==None:
                    time.sleep(2)
                    continue
            if s_conn.exists(usedkey):
                #devid=devID.decode(encoding='utf-8')
                #TestInsertToPostgresql()
                if is4grun==0:
                    SysIni4G()
                try:
                    ser = socket.socket()
                    ser.settimeout(5)
                    ser.connect((sysdict['sip1'], 9999))  # 12348
                    ser.settimeout(None)
                    epc = s_conn.zrange(usedkey, 0, -1)
                    print ('to postgresql')
                    #InsertToPostgresql(devID,epc)
                    #devs = b'DEVID:' + devID + b';NUMS:' + str(len(epc)).encode(encoding='utf-8') + b';'
                    #print(devs+usedkey)
                    #ser.sendall(devs)
                    print(epc)
                    for var in epc:
                        sdevs=b'DEVID:' + devID + b';'+var + b';'
                        ser.sendall(sdevs)#ser.sendall(var + b';')
                    ser.close()
                    s_conn.delete(usedkey)
                    usedkey=''
                    time.sleep(1)
                except:
                    is4grun=0
                    #time.sleep(1)
                    continue
            else:
                usedkey=''
                continue
        time.sleep(2)




def EPCToSqueue(pool=None,keyname='EPCDatasqueuekey'):
    global edataqueueformat
    try:
        conn=redis.Redis(host = '127.0.0.1', password = '123456', port = 6379, db = 1)
        if conn.ping():
            print('conn ok')
        else:
            print('shawanyi')
    except:  #
        return False

    usdnewkeyname='devIDEPC-%d' % (edataqueueformat)
    print('EPCToSqueue:'+usdnewkeyname)
    edataqueueformat=(edataqueueformat+1)%10
#    if conn==None:
#        conn = redisconnpool
    if conn.exists('devIDEPC'):

        if conn.exists(usdnewkeyname):
            conn.delete(usdnewkeyname)

        try:
            pipe = conn.pipeline()
            #pipe.watch(usedkey)
            pipe.multi()
            pipe.rename('devIDEPC',usdnewkeyname)
            pipe.expire(usdnewkeyname,1800)
            pipe.rpush(keyname,usdnewkeyname)
            pipe.execute()
        except:
            print('pipe EPCToSqueue err')
            return False
        #else:
#        conn.rename('devIDEPC',usdnewkeyname)
#        conn.expire(usdnewkeyname,1800)
#        conn.rpush(keyname,usdnewkeyname)
        return True
    else:
        return False

def EPCProsseRedis1():
    global EPCProsseRedisflg
    EPCProsseRedisflg += 1
    if EPCProsseRedisflg > int(sysdict['ss']):#int(sysdict['ts']):  # 30:
        EPCProsseRedisflg = 0
        return (EPCToSqueue(pool=redisconnpool,keyname='EPCDatasqueuekey'))

        if redisconnpool != None:
            return(EPCToSqueue(pool=redisconnpool,keyname='EPCDatasqueuekey'))

def EPCProsseRedis():
    global EPCProsseRedisflg
    EPCProsseRedisflg += 1
    if EPCProsseRedisflg > int(sysdict['ss']):#int(sysdict['ts']):  # 30:
        EPCProsseRedisflg = 0
        if redisconnpool != None:
            epc = redisconnpool.zrange('devIDEPC', 0, -1)
            devs = b'DEVID:' + devID + b';NUMS:' + str(len(epc)).encode(encoding='utf-8') + b';'
            try:
                ser = socket.socket()
                ser.settimeout(5)
                ser.connect((sysdict['sip1'], 9999))  # 12348
                ser.settimeout(None)
                ser.sendall(devs)  # ser.sendall(b'DEVID:'+devID)
                for var in epc:
                    ser.sendall(var + b';')
                ser.close()
            except:
                print('socket ERR:{0};{1}'.format(sysdict['sip1'],9999))
                #loggererro.debug('socket ERR:{0};{1}'.format(sysduct['sip1'],9999))
            print(redisconnpool.zrange('devIDEPC', 0, -1))
            redisconnpool.zremrangebyscore('devIDEPC', 1, 1)
    
    
def RfidCallbackprossData1(data):
    global rfidcallbackProssdata
    global RfidCMD
    global e
    global issysset
    s=-1
    end=0
    print ('rfidcallbackProssdata:{0}'.format(rfidcallbackProssdata))
    if data.find(b'\xff')!=0:
        if len(rfidcallbackProssdata)>0:
            rfidcallbackProssdata+=data
    else:
        
        rfidcallbackProssdata=data
    print ('rfidcallbackProssdata-1:{0}'.format(rfidcallbackProssdata))
    
#    if issysset==107:
#        issysset=7
#        return
        
    while True:
        s=rfidcallbackProssdata.find(b'\xff',end)
        if s==-1:
            rfidcallbackProssdata=b''
            break
        end=rfidcallbackProssdata.find(b'\xff',s+1)
        if end==-1:
            Muldata=rfidcallbackProssdata[s:]
        else:
            Muldata=rfidcallbackProssdata[s:end]
        
        print ('Muldata:{0}'.format(Muldata))
        ret=RfidCMD.ProcessorData(Muldata)
        print('ProcessorData DevID{0}'.format(devID))
        print('Pro ok:{0},{1}'.format(ret[0], ret[1]))
        if ret[0]>0:
            ProssAll(ret[1])
        else:
            if end==-1:
                rfidcallbackProssdata=Muldata
                break
            else:
                while True:
                    end=rfidcallbackProssdata.find(b'\xff',end+1)
                    if end==-1:
                        Muldata=rfidcallbackProssdata[s:end]
                    else:
                        Muldata=rfidcallbackProssdata[s:end]
                    print ('Muldata1:{0}'.format(Muldata))
                    ret=RfidCMD.ProcessorData(Muldata)
                    if ret[0]>0:
                        print('ProcessorData DevID{0}'.format(devID))
                        print('Pro ok:{0},{1}'.format(ret[0], ret[1]))
                        ProssAll(ret[1])
                        break
                    else:
                        if end==-1:
                            rfidcallbackProssdata=Muldata
                            return
                    if end==-1:
                        rfidcallbackProssdata=b''
                        return

        if end==-1:
            rfidcallbackProssdata=b''
            break
    
def comrecvcallbackpross(data):
    global RfidCMD
    global e
    
    #logger.debug('comrecvcallbackpross data:{0}'.format(data))
    RfidCallbackprossData(data)
    return
    
    ret=RfidCMD.ProcessorData(data)
    print('ProcessorData')
    print('Pro ok:{0},{1}'.format(ret[0], ret[1]))
    if ret[0]>0:
        ProssAll(ret[1])
        
e=EmbeddedCom.ComCOMThread(Port='/dev/ttyS4',baudrate=115200,timeout=0.1,RCallarg=rfidcallbackdata,ReceiveCallBack=comrecvcallbackpross)
tag22rev=0
tag29rev=0


def ProssCommand(data):
    global issysset
    global devID
    global e
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


def SysCommand(q, flg=0):
    global issysset
    while True:
        msg = q.get_nowait()
        print(msg)
        if msg != None:
            if msg == b'Rfidstop':
                issysset = 199
                q.put_extend('RfidControlAnswer', 'RfidstopOK')
                break
            elif msg == b'Rfidstart':
                issysset = 0;
                q.put_extend('RfidControlAnswer', 'RfidstartOK')
                if not SysIni():
                    print('SysIni Erro')
                    break
        if flg == 1:
            break
        else:
            time.sleep(2)


def SysCommand1(q):
    global issysset
    msg = q.get_nowait()
    print(msg)
    if msg != None:
        if msg == b'Rfidstop':
            issysset = 199
            q.put_extend('RfidControlAnswer', 'RfidstopOK')

        elif msg == b'Rfidstart':
            issysset = 0;
            q.put_extend('RfidControlAnswer', 'RfidstartOK')
            if not SysIni():
                print('SysIni Erro')


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
    q = RedisQueue(name='RfidControl', pool=pool)
    if not q.istrue:
        e.CloseSerialCOM()
        print('CloseSerialCOM 0')
        return
    #    while True:
    #        msg = q.get_nowait()
    #        print(msg)
    #        if msg != None:
    #            if msg==b'Rfidstop':
    #                issysset=199
    #                q.put_extend('RfidControlAnswer','RfidstopOK')
    #               break
    #            elif msg==b'Rfidstart':
    #                issysset=0;
    #                q.put_extend('RfidControlAnswer','RfidstartOK')
    #                break
    #        time.sleep(2)
    #    while True:
    #        SysCommand1(q)
    #        time.sleep(2)
    epcsendthreadalive = 1
    thread_sendepc = threading.Thread(target=EPCSendToServerThread, name='EPCSendToServerThread')
    thread_sendepc.setDaemon(True)
    thread_sendepc.start()

    while issysset < 200:
        # msg = redis_sub.parse_response()
        msg = q.get_nowait()
        if msg != None:
            print(msg)
            if msg == b'Rfidstop':
                issysset = 199
                q.put_extend('RfidControlAnswer', 'RfidstopOK')
            elif msg == b'Rfidstart':
                issysset = 0;
                q.put_extend('RfidControlAnswer', 'RfidstartOK')
        #        SysCommand1(q)
        # SysCommand(q=q,flg=1)

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
            # if usedAnt==1:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=usedAnt,ant2=0,ant3=0,ant4=0)
            # elif usedAnt==2:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=0,ant2=usedAnt,ant3=0,ant4=0)
            # elif usedAnt==3:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=0,ant2=0,ant3=usedAnt,ant4=0)
            # elif usedAnt==4:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=0,ant2=0,ant3=0,ant4=usedAnt)
            # else:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=1,ant2=0,ant3=0,ant4=0)
            sendcmd = RfidCMD.SetAntEnable(ant1=int(sysdict['a1']), ant2=int(sysdict['a2']), ant3=int(sysdict['a3']),
                                           ant4=int(sysdict['a4']))
            print('SetAntEnable:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 10:
            # if usedAnt==1:
            #    sendcmd=RfidCMD.SetAntPower(ant1=usedAnt,ant2=0,ant3=0,ant4=0,rpower=usedPower)
            # elif usedAnt==2:
            #    sendcmd=RfidCMD.SetAntPower(ant1=0,ant2=usedAnt,ant3=0,ant4=0,rpower=usedPower)
            # elif usedAnt==3:
            #    sendcmd=RfidCMD.SetAntPower(ant1=0,ant2=0,ant3=usedAnt,ant4=0,rpower=usedPower)
            # elif usedAnt==4:
            #    sendcmd=RfidCMD.SetAntPower(ant1=0,ant2=0,ant3=0,ant4=usedAnt,rpower=usedPower)
            # else:
            #    sendcmd=RfidCMD.SetAntPower()
            sendcmd = RfidCMD.SetAntPower(ant1=int(sysdict['a1']), ant2=int(sysdict['a2']), ant3=int(sysdict['a3']),
                                          ant4=int(sysdict['a4']), rpower=int(sysdict['aw']))
            print('SetAntPower:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        else:
            time.sleep(sl)  # time.sleep(2)


def main():
    test = RFIDReadAndWrite(comrecvcallbackpross)
    global e
    # data=b''
    # e=EmbeddedCom.ComCOMThread(Port='/dev/ttyUSB0',baudrate=115200,timeout=0.5,RCallarg=data,ReceiveCallBack=comrecvcallbackpross)
    e.TestCallBack()
    if e.RunAllStart():
        pass
    else:
        print('RunAllStart ERR')
        return

    testAnt = 1
    if testAnt == 1:
        time.sleep(5)
        # ttt=command=RfidCMD.BtoApp()
        # ttt=command=RfidCMD.GetTagMultiple()
        ttt = command = RfidCMD.SubSetGetTagData()
        print('BtoApp:{0},{1}'.format(ttt[0], ttt[1]))
        send = e.WriteSerialCOM(ttt[1])
        print(send)
        #        tss=b'\xff\x05"\x00\x00\x00\x00\xc8\x08\x77'
        #        #tss=b'\xff\x01a\x00\xbd\xbd'#0x61 获得天线接口配置信息
        #        send=e.WriteSerialCOM(tss)
        #        print(tss)
        while True:
            time.sleep(5)

    time.sleep(5)
    command = RfidCMD.GetTagMultiple()
    print('ok:{0},{1}'.format(command[0], command[1]))
    if command[0]:
        send = e.WriteSerialCOM(command[1])
        print('send:{0}:{1},'.format(command[0], command[1]))

    while True:
        time.sleep(5)
        # command=RfidCMD.GetDNum()
        # command=RfidCMD.IsAppoBootLoad()
        # command=RfidCMD.BtoApp()
        # command=RfidCMD.SetAntEnable(0,0,3,0)
        command = RfidCMD.GetTagMultipleCommand()
        print('ok:{0},{1}'.format(command[0], command[1]))
        if command[0]:
            send = e.WriteSerialCOM(command[1])
            print('send:{0}:{1},'.format(command[0], command[1]))


if __name__ == '__main__':
    RFIDGetTagStarOrNotSub(0)  # RFIDGetTagStart()#main()
