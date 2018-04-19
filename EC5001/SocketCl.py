# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 12:29:15 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import socket
import time

so4gpath="./libEC20.so"
ll = ctypes.cdll.LoadLibrary
lib = ll(so4gpath)

#funec20ini=lib.EC20_init
funec20inirun=lib.EC20_init_run
funec20inirun.restype = c_int
funec20shutdown=lib.EC20_Shutdown
funec20shutdown.restype = c_int


def send_e():
    print('start to set EC20...')
    #funec20ini()
    ret=funec20inirun()
    if ret < 0:
       print('start EC20 Err')
       return
    print('end to set EC20')
    ser = socket.socket()
    ser.connect(('218.240.49.25', 9999))#ser.connect(('127.0.0.1', 9999))  # 12348
    ser.sendall(b'13213415')
    #ser.sendall('exit')
    ser.close()
    time.sleep(2)
    ret=funec20shutdown()
    print (ret)
def send_exit():
    ser = socket.socket()
    ser.connect(('127.0.0.1', 9999))  # 12348
    #ser.sendall(b'13213415')
    ser.sendall(b'exit')
    ser.close()
if __name__ == '__main__':
    send_e()
    #send_exit()
    
    
'''    
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Colin Yao
#客户端
import socket
client = socket.socket() #定义协议类型,相当于生命socket类型,同时生成socket连接对象
client.connect(('127.0.0.1',9999))
while True:
 
    msg = input(">>>").strip()
    if len(msg) ==0:
        continue
    if 'exit' in msg:
        break
    client.send(msg.encode("utf-8"))
    data = client.recv(1024)#这里是字节1k
    print("recv:>",data.decode())
client.close()
'''
