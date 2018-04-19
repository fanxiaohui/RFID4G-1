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
import threading

erdata=b''
def comrecvcallbackpross(data):
    print('e rev :{0}'.format(data))

e = EmbeddedCom.ComCOMThread(Port='/dev/ttyAMA3', baudrate=115200, timeout=0.1, RCallarg=erdata,
                             ReceiveCallBack=comrecvcallbackpross)

#e2 = EmbeddedCom.ComCOMThread(Port='/dev/ttyAMA4', baudrate=115200, timeout=0.1, RCallarg=None,
#                             ReceiveCallBack=None)


def EPCSendToServerThread():
    e2send = b'abcdefgaaafjaglkagkalkjgkaka;jkgjagjka;dajgkajkakgjajgaklakl;jgajgajabcdefg'
    e2 = EmbeddedCom.ComCOMThread(Port='/dev/ttyAMA4', baudrate=115200, timeout=0.1, RCallarg=None,
                                  ReceiveCallBack=None)
    while True:
        e2.WriteSerialCOM(e2send)
        print ('e2 send:{0}'.format(e2send))
        getrevdata=e2.ReadDataFromSerialCOMTimeout(TimeOut=100)
        print('e2 rev:{0}'.format(getrevdata))
        #print('-------------------------')
        time.sleep(1)


def RunMain():
    esend=b'1234567890123456789012345678901234567890123456789012234567890'
    #e2send=b'0987654321'
    if e.RunAllStart():
        e.WriteSerialCOM(esend)
    #if e2.RunAllStart():
    #    e2.WriteSerialCOM(e2send)
#    thread_sendepc = threading.Thread(target=EPCSendToServerThread, name='EPCSendToServerThread')
#    thread_sendepc.setDaemon(True)
#    thread_sendepc.start()
    while True:
        print(e.WriteSerialCOM(esend))
    #    e2.WriteSerialCOM(e2send)
        time.sleep(0.2)

    pass

if __name__ == '__main__':
    RunMain()
