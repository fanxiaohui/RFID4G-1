# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:09:19 2018

@author: root
"""

import sys
import ctypes
from ctypes import *
#	uint8 BootLoadToApp(uint8 * pOutbuf);//0X04
#	uint8 SetBaudRate(uint8 * pOutbuf, int BaudRate);//0X06
#	uint8 AppToBootLoad(uint8 * pOutbuf);//0X09
#	uint8 GetDeviceNum(uint8 * pOutbuf);//0X10
#	uint8 isAppOrBootLoad(uint8 * pOutbuf);//0X0C
#	uint8 GetTagMultiple(uint8 * pOutbuf, uint16 msTimes, uint16 SearchFlags);//0X22:多标签盘存命令，READ TAG MULTIPLE
#	uint8 GetTagMultipleCommand(uint8 * pOutbuf); //0X29: 获取盘存到标签信息命令
#	uint8 SetAntEnable(uint8 * pOutbuf, uint8 ant1, uint8 ant2, uint8 ant3, uint8 ant4);
#	uint8 SetAntPower(uint8 * pOutbuf, uint8 ant1, uint8 ant2, uint8 ant3, uint8 ant4, uint16 rpower, uint16 wpower, uint16 stime);
#	uint8 SubSetGetTagData(uint8 * pOut, uint8 timesm);
#	uint8 SubSetGetTagDataStop(uint8 * pOut);

#	//uint8 GetBOOTLOADERorFIRMWARE(uint8 * pOutbuf);
#	uint16 ProcessorData(uint8 * pOutBuf, uint8 * pPdata, uint16 pdatalen);//串口接收处理

class RfidCMDAnalysis(object):
    def __init__(self,SoPath="./libRfidcom.so"):
        self.sopath=SoPath
        self.ll = ctypes.cdll.LoadLibrary
        self.lib = self.ll(SoPath)
        self.dd = c_ubyte * 10240
        self.dest = self.dd()

##call
        self.funBtoApp=self.lib.BootLoadToApp
        self.funBtoApp.restype = c_ubyte
#funBtoApp.argtypes = [c_char_p]
#dll.addf.argtypes = (c_float, c_float)

        self.funSBR=self.lib.SetBaudRate
        self.funSBR.restype = c_ubyte

        self.funApptoB=self.lib.AppToBootLoad
        self.funApptoB.restype = c_ubyte

        self.funGetDNum=self.lib.GetDeviceNum
        self.funGetDNum.restype = c_ubyte

        self.funisAoBL=self.lib.isAppOrBootLoad
        self.funisAoBL.restype = c_ubyte

        self.funGetTagMultiple=self.lib.GetTagMultiple
        self.funGetTagMultiple.restype = c_ubyte

        self.funGetTagMultipleCommand=self.lib.GetTagMultipleCommand
        self.funGetTagMultipleCommand.restype = c_ubyte

        self.funSetAntEnable=self.lib.SetAntEnable
        self.funSetAntEnable.restype = c_ubyte
#funSetAntEnable.argtypes = (,c_int,c_int,c_int,c_int)

        self.funSetAntPower=self.lib.SetAntPower
        self.funSetAntPower.restype = c_ubyte

        self.funSubSetGetTagData=self.lib.SubSetGetTagData
        self.funSubSetGetTagData.restype = c_ubyte

        self.funSubSetGetTagDataStop=self.lib.SubSetGetTagDataStop
        self.funSubSetGetTagDataStop.restype = c_ubyte

        self.funProcessorData=self.lib.ProcessorData
        self.funProcessorData.restype = c_uint

    def ApptoB(self):
        #global dest
        retstr=b''
        ret=0
        ret = self.funApptoB(byref(self.dest))
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr
 
    def SetBaudrate(self,baudrate):
        #global dest
        retstr=b''
        ret=0
        if isinstance(baudrate,int):
            if baudrate==9600 or baudrate==115200:
                pass
            else:
                return ret,retstr
        else:
            return ret,retstr
        ret = self.funSBR(byref(self.dest),baudrate)
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr
   
    def BtoApp(self):
       #global dest
       retstr=b''
       ret=0
       ret = self.funBtoApp(byref(self.dest))
       if ret != 0:
           retstr+=bytes(self.dest[:ret])
       return ret,retstr

    def GetDNum(self):
        retstr=b''
        ret=0
        ret = self.funGetDNum(byref(self.dest))
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr
 
    def IsAppoBootLoad(self):  
        retstr=b''
        ret=0
        ret = self.funisAoBL(byref(self.dest))
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def GetTagMultiple(self,msTime=500,searchflg=0):
        retstr=b''
        ret=0
        ret = self.funGetTagMultiple(byref(self.dest),msTime,searchflg)
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def GetTagMultipleCommand(self):
        retstr=b''
        ret=0
        ret = self.funGetTagMultipleCommand(byref(self.dest))
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def SetAntEnable(self,ant1=1,ant2=2,ant3=3,ant4=4):
        retstr=b''
        ret=0
        ret = self.funSetAntEnable(byref(self.dest),ant1,ant2,ant3,ant4)
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def SetAntPower(self,ant1=1,ant2=2,ant3=3,ant4=4,rpower=1024,wpower=3000,stime=500):    
        retstr=b''
        ret=0
        ret = self.funSetAntPower(byref(self.dest),ant1,ant2,ant3,ant4,rpower,wpower,stime)
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def SubSetGetTagData(self,timesm=5):
        retstr=b''
        ret=0
        ret = self.funSubSetGetTagData(byref(self.dest),timesm)
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def SubSetGetTagDataStop(self):
        retstr=b''
        ret=0
        ret = self.funSubSetGetTagDataStop(byref(self.dest))
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr

    def ProcessorData(self,data):
        retstr=b''
        ret=0
#        rrev = c_ubyte * len(data)#255
#        rev = rrev()
#        index=0
#        for z in data:
#            rev[index]=z
#            index+=1
            
        #ret = self.funProcessorData(byref(self.dest),byref(rev),len(data))
        ret = self.funProcessorData(byref(self.dest),cast(data, POINTER(c_ubyte)),len(data))
        if ret != 0:
            retstr+=bytes(self.dest[:ret])
        return ret,retstr
    
def maintest():
    rt=RfidCMDAnalysis()
    q=b'Status'
    recv=b'\xff\x01\x0c\x00\x00\x12\x63\x43'
    justtest=rt.ProcessorData(recv)
    print('ProcessorData')
    print('ok:{0},{1}'.format(justtest[0], justtest[1]))
    if q in justtest[1]:
        print (q)
    
if __name__ == '__main__':
    maintest()
