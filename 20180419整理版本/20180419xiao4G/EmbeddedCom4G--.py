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

        self.threadLock=threading.Lock()
        self.qworkqueue=queue.Queue(10)
        
        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg
        
        print(self.port)
        
    def SetReceiveCallBack(self,arg,function):
        self.rcallarg=arg
        self.receivecallback=function
        
    def ComThreadReceiveCallBack(self):
        if self.receivecallback!=None:
            return self.receivecallback(self.rcallarg)
            
    def TestCallBack(self):
        if self.receivecallback!=None:
            self.rcallarg=b'renzhendian,ceshinne'
            return self.ComThreadReceiveCallBack()

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

    def ReadSerialCOM(self):
        if self.iscomopen:
            while self.threadalive:
                tout=b''
                time.sleep(0.01)
                n=self.l_serial.inWaiting()
                while n:
                    rfidReadBuf=self.l_serial.readall()#rfidReadBuf=self.l_serial.read(n)
                    tout+=rfidReadBuf
                    #time.sleep(0.01)
                    n=self.l_serial.inWaiting()
                if len(tout)>0:
                    self.threadLock.acquire()
                    if self.qworkqueue.full():
                        print("qworkqueue00000000")
                    self.qworkqueue.put(tout)
                    print ('qworkqueue size : {0},tounum: {1}'.format(self.qworkqueue.qsize(), len(tout)))
                    self.threadLock.release()
                    print('tout{0},{1}'.format(tout,len(tout)))
                else:
                    continue
        print("ReadSerialCOM END")
            
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
        
    def StartReadThread(self):
        if not self.iscomopen:
            if not self.OpenSerialCOM():
                return False
        if self.iscomopen and self.thread_read==None:
            self.threadalive=True
            self.thread_read_flg=True
            self.thread_read=threading.Thread(target=self.ReadSerialCOM,name='ReadSerialCOM4G'+self.port)
            self.thread_read.setDaemon(True)
            self.thread_read.start()
            return True

    def ProcessThread(self):
        if self.thread_process==None:
            self.thread_process_flg=True
            self.threadalive=True
            self.thread_process=threading.Thread(target=self.AllProcess,name='AllProcess4G'+self.port)
            self.thread_process.setDaemon(True)
            self.thread_process.start()
            return True
            
    def StopThread(self):
        self.threadalive=False
        if self.thread_read_flg:
            self.thread_read.join()
            self.thread_read=None
        else:
            pass
        if self.thread_process_flg:
            self.thread_process.join()
            self.thread_process=None
        else:
            pass
        
    def RunAllStart(self):
        if self.OpenSerialCOM():
            try:
                if self.StartReadThread():
                    print ("StartReadThread")
                else:
                    print ("StartReadThread err")
                    return False
                if self.ProcessThread():
                    print ("ProcessThread")
                else:
                    self.StopThread()
                    print ("ProcessThread err")
                    return False
            except Exception as se:
                print(str(se))
                return False
        else:
            print ("OpenSerialCOM err")
            return False
        return True
        
    def AllProcess(self):
        if self.iscomopen:
            while self.threadalive:
                time.sleep(0.01)
                self.threadLock.acquire()
                if not self.qworkqueue.empty():
                    if self.receivecallback!=None:
                        self.rcallarg=self.qworkqueue.get()
                    else:
                        data=self.qworkqueue.get()
                    self.threadLock.release()
                    
                    if self.receivecallback!=None:
                        self.ComThreadReceiveCallBack()
                        print('callback:{0}'.format(self.rcallarg,))
                    else:
                        print(data)
                else:
                    self.threadLock.release()

'''
    def AllProcess(self):
        if self.iscomopen:
            while self.threadalive:
                time.sleep(0.01)
                self.threadLock.acquire()
                if not self.qworkqueue.empty():
                    data=self.qworkqueue.get()
                    self.threadLock.release()
                    print(data)
                else:
                    self.threadLock.release()
'''

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
