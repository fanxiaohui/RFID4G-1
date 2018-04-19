# -*- coding: utf-8 -*-
"""
Created on Wed March 15 11:06:31 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import EmbeddedCom4G
#import CUartThread
import time


sys4gcmddict={'AT':'AT','Zreboot':'Z','devreboot':'REBOOT','issetopen':'E',
              'outcmd':'ENTM','workmod':'WKMOD','cmdPW':'CMDPW','Startinformation':'STMSG',
              'signalintensity':'CSQ','rstarttime':'RSTIM','networkinfo':'SYSINFO',
              'FactoryDefault':'RELD','ofsetting':'CLEAR','saveset':'CFGTF',
              'getver':'VER','getSN':'SN','getICCID':'ICCID','getIMEI':'IMEI',
              'UART':'UART','UARTFT':'UARTFT','UARTFL':'UARTFL','RFCEN':'RFCEN',
              'APN':'APN','SOCKA':'SOCKA','SOCKB':'SOCKB','SOCKC':'SOCKC',
              'SOCKD':'SOCKD','SOCKAEN':'SOCKAEN','SOCKBEN':'SOCKBEN','SOCKCEN':'SOCKCEN',
              'SOCKDEN':'SOCKDEN','SOCKASL':'SOCKASL','SOCKBSL':'SOCKBSL','SOCKCSL':'SOCKCSL',
              'SOCKDSL':'SOCKDSL','SOCKALK':'SOCKALK','SOCKBLK':'SOCKBLK','SOCKCLK':'SOCKCLK',
              'SOCKDLK':'SOCKDLK','SHORATO':'SHORATO','SHORBTO':'SHORBTO','SHORCTO':'SHORCTO',
              'SHORDTO':'SHORDTO','SOCKATO':'SOCKATO','SOCKBTO':'SOCKBTO','SOCKCTO':'SOCKCTO',
              'SOCKDTO':'SOCKDTO','SOCKIND':'SOCKIND','SDPEN':'SDPEN','REGEN':'REGEN',
              'REGTP':'REGTP','REGDT':'REGDT','REGSND':'REGSND','CLOUD':'CLOUD',
              'HEARTEN':'HEARTEN','HEARTDT':'HEARTDT','HEARTSND':'HEARTSND','HEARTTM':'HEARTTM',
              'HTPTP':'HTPTP','HTPURL':'HTPURL','HTPSV':'HTPSV','HTPHD':'HTPHD','HTPTO':'HTPTO',
              'HTPFLT':'HTPFLT','SMSEND':'SMSEND','CISMSSEND':'CISMSSEND'}
#sysdict={'commandkey':'usr.cn','DeviceRuninformation':'[USR-LTE-7S4]'}

#'\r\n'
class Com4GModularClass(object):
    def __init__(self,Port='/dev/ttySAC2',baudrate=115200,protocol='TCP',address='218.240.49.25',netport=9999,ReceiveCallBack=None,RCallarg=None):

        self.sysdict={'commandkey':'usr.cn','DeviceRuninformation':'[USR-LTE-7S4]'}
        self.comisopen=False
        self.comport=Port
        self.combaudrate=baudrate
        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg
        self.usedcom_callbackdata=b''
#        self.usedcom_4G=EmbeddedCom4G.ComCOMThread(Port=self.comport,baudrate=self.combaudrate,timeout=0.5,RCallarg=self.usedcom_callbackdata,ReceiveCallBack=self.usedcom_callbackpross)
        self.usedcom_4G=EmbeddedCom4G.ComCOMThread(Port=self.comport,baudrate=self.combaudrate,timeout=0.5,RCallarg=None,ReceiveCallBack=None)
        #        self.usedcom_4G=CUartThread.CUartThread(Port=self.comport,baudrate=self.combaudrate,RCallarg=self.usedcom_callbackdata,ReceiveCallBack=self.usedcom_callbackpross)
        self.is4gsysrun=0
        self.sysstate=0
        self.operationdict={'usingcmd':'','value':''}
        self.readtimesout=100

        self.pl=protocol
        self.ad=address
        self.netport=netport

    def usedcom_callbackpross(self,data):
        if self.is4gsysrun == 0:
            ffutf8 = self.sysdict['DeviceRuninformation'].encode(encoding='utf-8')
            if ffutf8 in data:
                self.is4gsysrun = 1
                print('4G Run OK')
                #self.GetCMDPW()
        else:
            if self.sysstate==200:
                if self.receivecallback!=None:
                    self.receivecallback(data)
                else:
                    pass
            else:
                pass


    def Get4GmodeStartFlg(self):
        if self.is4gsysrun == 0:

            ret=self.usedcom_4G.OpenSerialCOM()
            print (ret)
            if ret < 0:
                return 'ERR'
            self.comisopen=True
            print('Get4GmodeStartFlg')
            ffutf8 = self.sysdict['DeviceRuninformation'].encode(encoding='utf-8')
            revdata = b''
            while True:
                tdata=self.usedcom_4G.ReadDataFromSerialCOM()
                #print (tdata)
                if len(tdata)>0:
                    print (tdata)
                    if ffutf8 in tdata:
                        print('4G Run OK')
                        self.is4gsysrun=1
                        return 'OK'
                    #else:
                        #revdata+=tdata
                        #if ffutf8 in revdata:
                            #print('4G Run OK 1')
                            #self.is4gsysrun=1
                            #return 'OK'

    def SendCmdByAT(self,cmd,parameter=''):
        if self.is4gsysrun == 0:
            return 0
        self.operationdict['usingcmd'] = cmd
        cmdstr='AT+'+cmd+parameter+'\r'
        print (cmdstr)
        self.usedcom_4G.WriteSerialCOM(cmdstr.encode(encoding='utf-8'))
        #self.usedcom_4G.SendUart(cmdstr.encode(encoding='utf-8'))
        return 1

    def SendCmdByPassword(self,cmd,parameter=''):
        if self.is4gsysrun == 0:
            return 0
        self.operationdict['usingcmd']=cmd
        cmdstr=self.sysdict['commandkey']+'AT+'+cmd+parameter+'\r'
        print (cmdstr)
        self.usedcom_4G.WriteSerialCOM(cmdstr.encode(encoding='utf-8'))
        #self.usedcom_4G.SendUart(cmdstr.encode(encoding='utf-8'))
        return 1

    def RebootSoftware(self,mode=1):
        cmd=sys4gcmddict['Zreboot']
        print('RebootSoftware')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def RebootDevice(self,mode=1):
        cmd=sys4gcmddict['devreboot']
        print('RebootDevice')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def GetStatus(self,mode=1):
        if self.comisopen==False:
            return ''
        cmd=sys4gcmddict['issetopen']
        print ('GetStatus')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'+E' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return ''
        else:
            return ''

    def SetStatus(self,mode=1,status='ON'):
        if status == 'ON' or status == 'OFF':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['devreboot']
        print('SetStatus')
        if mode==0:
            self.SendCmdByAT(cmd,'='+status)
        else:
            self.SendCmdByPassword(cmd,'='+status)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def BackMode(self,mode=1):
        cmd=sys4gcmddict['outcmd']
        print('BackMode')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def GetWKMod(self,mode=1):
        cmd=sys4gcmddict['workmod']
        print('GetWKMod')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'+WKMOD' in getrevdata:
                if b'NET' in getrevdata:
                    return 'NET'
                elif b'HTTPD' in getrevdata:
                    return 'HTTPD'
                else:
                    return ''
        else:
            return ''

    def SetWKMod(self,mode=1,status='NET'):
        if status == 'NET' or status == 'HTTPD':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['workmod']
        print('SetWKMod')
        if mode==0:
            self.SendCmdByAT(cmd,'='+status)
        else:
            self.SendCmdByPassword(cmd,'='+status)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def GetCMDPW(self,mode=1):#...
        cmd=sys4gcmddict['cmdPW']
        print('GetCMDPW')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'+CMDPW' in getrevdata:
                return getrevdata
        else:
            return ''

    def SetCMDPW(self,mode=1,password='usr.cn'):
        cmd=sys4gcmddict['cmdPW']
        print('SetCMDPW')
        if mode==0:
            self.SendCmdByAT(cmd,'='+password)
        else:
            self.SendCmdByPassword(cmd,'='+password)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def SaveTodefault(self,mode=1):
        cmd=sys4gcmddict['saveset']
        print ('SaveTodefault')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def GetSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKA']
        print('GetSockA')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'+SOCKA' in getrevdata:
                return getrevdata
        else:
            return ''

    def SetSockA(self,mode=1,protocol='TCP',address='218.240.49.25',port=9999):
        if protocol == 'TCP' or protocol == 'UDP':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['SOCKA']
        print('SetSockA')
        if mode==0:
            self.SendCmdByAT(cmd,'='+protocol+','+address+','+str(port))
        else:
            self.SendCmdByPassword(cmd,'='+protocol+','+address+','+str(port))
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''


    def GetEnableSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKAEN']
        print('GetEnableSockA')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'+SOCKAEN' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return b''
        else:
            return ''


    def SetEnableSockA(self,mode=1,status='ON'):
        if status == 'ON' or status == 'OFF':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['SOCKAEN']
        print('SetEnableSockA')
        if mode==0:
            self.SendCmdByAT(cmd,'='+status)
        else:
            self.SendCmdByPassword(cmd,'='+status)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        else:
            return ''

    def GetLinkstatusSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKALK']
        print('GetLinkstatusSockA')
        if mode==0:
            self.SendCmdByAT(cmd)
        else:
            self.SendCmdByPassword(cmd)
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if len(getrevdata)>0:
            if b'+SOCKALK' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return ''
        else:
            return ''

        revdata = b''
        while True:
            tdata = self.usedcom_4G.ReadDataFromSerialCOM()
            if len(tdata)>0:
                revdata += tdata
                print(revdata)
                if b'+SOCKALK' in revdata:
                    if b'ON' in revdata:
                        return 'ON'
                    elif b'OFF' in revdata:
                        return 'OFF'
                    else:
                        pass

    def StartTcpUseSockA(self, mode=1, protocol='TCP', address='218.240.49.25', port=9999):
        ret = self.SetWKMod(mode=mode,status='NET')
        print('self.SetWKMod')
        print(ret)
        if ret != 'OK':
            return ret
        ret = self.SetEnableSockA(mode=mode,status='ON')
        print('self.SetEnableSockA')
        print(ret)
        if ret != 'OK':
            return ret
        ret = self.SetSockA(mode=mode, protocol=protocol, address=address, port=port)
        print('self.SetSockA')
        print(ret)
        if ret != 'OK':
            return ret
        #ret = self.RebootSoftware(mode=mode)
        #if ret != 'OK':
        #    return ret
        self.sysstate = 200

        self.pl = protocol
        self.ad = address
        self.netport = port
        time.sleep(1)
        return ret


    def Senddatasfornet(self,sddata):
        if self.sysstate!=200:
            if self.StartTcpUseSockA(mode=1,protocol=self.pl,address=self.ad,port=self.netport)!='OK':
                #time.sleep(2)
                return 0
        #comsenddata=sddata+'\r'
        #return self.usedcom_4G.WriteSerialCOM(sddata.encode(encoding='utf-8'))
        return self.usedcom_4G.WriteSerialCOM(sddata)

        #return self.usedcom_4G.SendUart(sddata)




def RunMain():
    data=b'1234567890'
    rt = Com4GModularClass(Port='/dev/ttyAMA4')



    #print(rt.OpenUart())
    state=rt.Get4GmodeStartFlg()
    if 'OK' in state:
        print(rt.GetStatus())
        #print(rt.StartTcpUseSockA())
        time.sleep(2)
        state=rt.Senddatasfornet(data)
        print (state)
    time.sleep(2)
    print(rt.SetEnableSockA(mode=1, status='OFF'))
    time.sleep(5)
    print(rt.StartTcpUseSockA())
    time.sleep(2)
    state = rt.Senddatasfornet(data)
    print(state)
    print('end')
    time.sleep(5)
    print(rt.SetEnableSockA(mode=1, status='OFF'))
    
    while True:
        time.sleep(1)


#    if rt.usedcom_4G.RunAllStart():
#        print("com ok")
#    else:
#        print('RFIDGetTagStart ERR Return')
#        return
#    while(1):
#        time.sleep(2)
#        #rt.GetCMDPW()
def RunMain1():
    rt = Com4GModularClass(Port='/dev/ttyAMA4')
    ret = rt.usedcom_4G.OpenSerialCOM()
    print(ret)
    if ret < 0:
        return 'ERR'
    rt.comisopen=True
    time.sleep(10)
    while True:
        print(rt.GetStatus())
        time.sleep(5)

if __name__ == '__main__':
    RunMain()
    #RunMain1()
