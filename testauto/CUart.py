# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:09:19 2018

@author: root
"""

import sys
import ctypes
from ctypes import *

#int UART_Open(int fd, char * port);
#void UART_Close(int fd);
#int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity);
#int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity);
#int UART_Recv(int fd, char * rcv_buf, int data_len);
#int UART_Send(int fd, char * send_buf, int data_len);

class CUart(object):
    def __init__(self,Port='/dev/ttyAMA3',baudrate=115200,ReceiveCallBack=None,RCallarg=None,SoPath="./CUart.so"):
        self.sopath=SoPath
        self.ll = ctypes.cdll.LoadLibrary
        self.lib = self.ll(SoPath)
        self.fd=-1
        self.port = Port
        self.baudrate = baudrate

        self.dd = c_ubyte * 10240
        self.dest = self.dd()

##call
        self.funUART_Open=self.lib.UART_OpenCom
        #self.funUART_Open=self.lib.UART_Open
        self.funUART_Open.restype = c_int

        self.funUART_Close=self.lib.UART_Close
        #self.funUART_Close.restype = c_int

        #self.funUART_Set=self.lib.UART_Set
        #self.funUART_Set.restype = c_int

        #self.funUART_Init=self.lib.UART_Init
        #self.funUART_Init.restype = c_int

        self.funUART_Recv=self.lib.UART_Recv
        self.funUART_Recv.restype = c_int

        self.funUART_Send=self.lib.UART_Send
        self.funUART_Send.restype = c_int

    def OpenUart(self):
        if self.fd>-1:
            self.CloseUart()
        #self.fd = self.funUART_Open(self.fd,self.port)
        #self.fd = self.funUART_Open(self.fd, self.port,self.baudrate)
        #print(self.port)
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
            if ret!=0:
                retstr+=bytes(self.dest[:ret])
            return ret, retstr
        else:
            return ret, retstr

    def SendUart(self,data):#cast(data, POINTER(c_ubyte)),len(data)
        ret=0
        if self.fd>-1:
            ret=self.funUART_Send(self.fd,cast(data, POINTER(c_byte)),len(data))
        return ret


def maintest():
    com = CUart(Port=b'/dev/ttyAMA3')
    ret=com.OpenUart()
    print('open com : {0}'.format(ret))
    if ret>-1:
        ret=com.SendUart(b'1234567890')
        if ret:
            while 1:
                ddd=com.RecvUart()
                print(ddd)
                if ddd:
                    com.CloseUart()
                    break

if __name__ == '__main__':
    maintest()
