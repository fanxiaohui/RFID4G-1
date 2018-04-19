# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 12:29:15 2018

@author: root
"""

import socket

def send_e():
    ser = socket.socket()
    ser.connect(('127.0.0.1', 9999))  # 12348
    ser.sendall(b'13213415')
    #ser.sendall('exit')
    ser.close()
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