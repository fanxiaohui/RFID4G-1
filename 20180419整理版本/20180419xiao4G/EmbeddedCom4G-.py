# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import serial
import threading
import time
#import string
#import binascii
import queue

class ComCOMThread(object):
    def __init__(self, Port='/dev/ttyAMA3',baudrate=115200,timeout=0.5,ReceiveCallBack=None,RCallarg=None):
        self.l_serial=serial.Serial()
        self.alive=False
        self.port=Port
        self.baudrate=baudrate
        self.timeout=timeout
        self.iscomopen=False
        self.threadalive=False

        self.thread_read=None
        self.thread_read_flg=False
        self.thread_process=None
        self.thread_process_flg=False

#        self.threadLock=threading.Lock()
#        self.qworkqueue=queue.Queue(10)
        
        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg
        
        print(self.port)
        
        
            

    def OpenSerialCOM(self):
        
        self.l_serial.port=self.port
        self.l_serial.baudrate=self.baudrate
        self.l_serial.timeout=self.timeout
        print (self.l_serial.port)
        try:
            self.l_serial.open()
            self.iscomopen=True
        except:
            print("Open Com ERR")
            print("")
            return False
        if self.l_serial.isOpen():
            return True
        else:
            return False
        
    def WriteSerialCOM(self,data):
        if self.iscomopen==False:
            if not self.OpenSerialCOM():
                return 0
        if isinstance(data,bytes):
            return self.l_serial.write(data)
        elif isinstance(data,str):
            return self.l_serial.write(data.encode(encoding='utf-8'))
        elif isinstance(data,int):
            return self.l_serial.write(bytes(data,))
        else:
            return 0
        #return self.l_serial.write(data)

    def ReadDataFromSerialCOM(self):
        if self.iscomopen:
            tout=b''
            time.sleep(0.5)
            #time.sleep(0.01)
            n=self.l_serial.inWaiting()
            while n:
                serialbuf=self.l_serial.read_all()
                tout+=serialbuf
                n=self.l_serial.inWaiting()
            return tout
        else:
            return b''

    def ReadDataFromSerialCOMTimeout(self,TimeOut=60):
        times=0
        rd=b''
        while True:
            gd=self.ReadDataFromSerialCOM()
            if len(gd)>0:
                times=0
                rd+=gd
                #return rd
            else:
                times+=1
                if times >= TimeOut:
                    print(times)
                    return rd

            
    def CloseSerialCOM(self):
        self.StopThread()
        if self.iscomopen == False:
            print ("not com to close")
            print ("")
            return False
        while self.l_serial.isOpen():
            self.l_serial.close()
        if self.l_serial.isOpen():
            print ("Close com fail")
            print ("")
        else:
            self.iscomopen=False
            print ("Close com OK")
            print ("")
        
        

def RunMain1():
    sd=b'123456'
    rt = ComCOMThread(Port='/dev/ttyAMA4')
    ret = rt.OpenSerialCOM()
    print(ret)
    if ret < 0:
        return 'ERR'
    while True:
        data=rt.ReadDataFromSerialCOMTimeout(TimeOut=100)
        print (data)

def RunMain():
    pass
    sd=b'123456'
    rt=ComCOMThread(Port='/dev/ttyAMA4')
    if rt.RunAllStart():
        pass
    else:
        return
    while True:
       # rt.WriteSerialCOM(sd)
        time.sleep(2)

if __name__ == '__main__':
    RunMain()
    #RunMain1()
