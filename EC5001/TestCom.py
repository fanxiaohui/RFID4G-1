# -*- coding: utf-8 -*-

import sys
import ctypes
from ctypes import *
import time

import EmbeddedCom

rfidcallbackdata=b''

def comrecvcallbackpross(data):
    global e
    
    print(data)

e=EmbeddedCom.ComCOMThread(Port='/dev/ttySAC2',baudrate=115200,timeout=0.1,RCallarg=rfidcallbackdata,ReceiveCallBack=comrecvcallbackpross)

def main():
    global e
    if e.RunAllStart():
        pass
    else:
        print('RunAllStart ERR')
        return
    while True:
        time.sleep(5)
        send=e.WriteSerialCOM(b'123456')
        print(send)

if __name__ == '__main__':
    main()
