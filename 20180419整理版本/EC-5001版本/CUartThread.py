# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:09:19 2018

@author: root
"""

import sys
import ctypes
from ctypes import *
import threading
import time
import queue


class CUartThread(object):
    def __init__(self,Port='/dev/ttyAMA3',baudrate=115200,ReceiveCallBack=None,RCallarg=None,SoPath="./CUart.so"):
        self.sopath=SoPath
        self.ll = ctypes.cdll.LoadLibrary
        self.lib = self.ll(SoPath)
        self.fd=-1
        self.port = Port
        self.baudrate = baudrate

        self.dd = c_ubyte * 10240
        self.dest = self.dd()

        self.threadalive = False
        self.thread_read=None
        self.thread_read_flg=False
        self.thread_process=None
        self.thread_process_flg=False

        self.threadLock=threading.Lock()
        self.qworkqueue=queue.Queue(10)

        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg

##call
        self.funUART_Open=self.lib.UART_OpenCom
        self.funUART_Open.restype = c_int

        self.funUART_Close=self.lib.UART_Close

        self.funUART_Recv=self.lib.UART_Recv
        self.funUART_Recv.restype = c_int

        self.funUART_Send=self.lib.UART_Send
        self.funUART_Send.restype = c_int

    def OpenUart(self):
        if self.fd>-1:
            self.CloseUart()
        self.fd = self.funUART_Open(self.fd, cast(self.port, POINTER(c_byte)), self.baudrate)
        return self.fd

    def CloseUart(self):
        if self.fd>-1:
            self.funUART_Close(self.fd)
            self.fd=-1

    def RecvUart(self):
        ret=0
        retstr=b''
        if self.fd>-1:
            ret=self.funUART_Recv(self.fd,byref(self.dest),1024)
            if ret>0:
                retstr+=bytes(self.dest[:ret])
            return ret, retstr
        else:
            return ret, retstr

    def SendUart(self,data):#cast(data, POINTER(c_ubyte)),len(data)
        ret=0
        if self.fd>-1:
            ret=self.funUART_Send(self.fd,cast(data, POINTER(c_byte)),len(data))
        return ret

    def ComThreadReceiveCallBack(self):
        if self.receivecallback!=None:
            return self.receivecallback(self.rcallarg)

    def RecvUartThread(self):
        if self.fd < 0:
            return
        while self.threadalive:
            tout = b''
            revnums = self.funUART_Recv(self.fd,byref(self.dest),1024)
            if revnums > 0:
                tout += bytes(self.dest[:revnums])
            if len(tout)>0:
                self.threadLock.acquire()
                if self.qworkqueue.full():
                    print("qworkqueue00000000")
                self.qworkqueue.put(tout)
                print ('qworkqueue size : {0},tounum: {1}'.format(self.qworkqueue.qsize(), len(tout)))
                self.threadLock.release()
                print('tout{0},{1}'.format(tout,len(tout)))
            else:
                time.sleep(0.05)
                continue
        print("ReadSerialCOM END")

    def ProcessDataThread(self):
        if self.fd>-1:
            while self.threadalive:
                time.sleep(0.05)
                self.threadLock.acquire()
                if not self.qworkqueue.empty():
                    if self.receivecallback != None:
                        self.rcallarg = self.qworkqueue.get()
                    else:
                        data = self.qworkqueue.get()
                    self.threadLock.release()

                    if self.receivecallback != None:
                        self.ComThreadReceiveCallBack()
                        print('callback:{0}'.format(self.rcallarg, ))
                    else:
                        print(data)
                else:
                    self.threadLock.release()

    def StartReadThread(self):
        if self.fd < 0:
            if self.OpenUart() < 0:
                return False
        if self.fd > -1 and self.thread_read == None:
            self.threadalive = True
            self.thread_read_flg = True
            self.thread_read = threading.Thread(target=self.RecvUartThread, name='RecvUartThread')
            self.thread_read.setDaemon(True)
            self.thread_read.start()
            return True

    def ProcessThread(self):
        if self.thread_process == None:
            self.thread_process_flg = True
            self.threadalive = True
            self.thread_process = threading.Thread(target=self.ProcessDataThread, name='ProcessDataThread')
            self.thread_process.setDaemon(True)
            self.thread_process.start()
            return True

    def StopThread(self):
        self.threadalive = False
        if self.thread_read_flg:
            self.thread_read.join()
            self.thread_read = None
        else:
            pass
        if self.thread_process_flg:
            self.thread_process.join()
            self.thread_process = None
        else:
            pass

    def RunAllStart(self):
        if self.OpenUart()>-1:
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


def maintest():
    com = CUartThread(Port=b'/dev/ttySAC2')
    if com.RunAllStart():
        while True:
            t=com.SendUart(b'1234567890')
            print(t)
            time.sleep(2)


    ret=com.OpenUart()
    print('open com : {0}'.format(ret))
    if ret>-1:
        ret=com.SendUart(b'1234567890')
        print(ret)
        if ret>0:
            while 1:
                ddd=com.RecvUart()
                print(ddd)
                if ddd:
                    com.CloseUart()
                    break

if __name__ == '__main__':
    maintest()
