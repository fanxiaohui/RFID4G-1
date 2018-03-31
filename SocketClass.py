# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 12:00:09 2018

@author: root
"""


#!/usr/bin/env python
# coding=utf-8

import socketserver
class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def handle(self):
        print ('running')
        while True:
            try:
                data = self.request.recv(1024)
                if(data==b''):
                    continue
                print (data)
                if data == b'exit':
                    print ('exit')
                    self.server.shutdown()
                    self.request.close()
                    break

            except Exception as e:
                self.server.shutdown()
                self.request.close()
                break

if __name__ == '__main__':
    # socketserver的多进程非阻塞启动
    server = socketserver.ThreadingTCPServer(('localhost',9999),RequestHandler)
    server.serve_forever()


'''
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Colin Yao

import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):  #所有请求的交互都是在handle里执行的,
        while True:
            try:
                self.data = self.request.recv(1024).strip()#每一个请求都会实例化MyTCPHandler(socketserver.BaseRequestHandler):
                print("{} wrote:".format(self.client_address[0]))
                print(self.data)
                self.request.sendall(self.data.upper())#sendall是重复调用send.
            except ConnectionResetError as e:
                print("err ",e)
                break

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999 #windows
    #HOST, PORT = "0.0.0.0", 9999 #Linux
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)   #线程
    server.serve_forever()
'''

'''
import sys
import socket
import ctypes
from ctypes import *
import threading

class RfidSocketClass(object):
    def __init__(self, ip='127.0.0.1',tport=8888,flg=0,lport=9999,ReceiveCallBack=None,RCallarg=None):
        self.ip=ip
        self.tport=tport
        self.lport=lport
        self.flg=flg
        self.s=None
        self.host = socket.gethostname()
        
        self.thread_process_flg=False
        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg

        if flg==0:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def netrecv():
        if self.receivecallback!=None:
            return self.receivecallback(self.rcallarg)
        
        
    def Connect(self):
        if self.flg==0:
            #ss=self.s
            self.s.bind((self.host, self.lport))
            #self.s.listen(5)
        else:
            self.s.connect((self.ip,self.tport))
            
        
def RunMain():
    
    rt=RfidSocketClass(ip='127.0.0.q',tport=8888,flg=0,lport=9999)
    rt.Connect()

if __name__ == '__main__':
    RunMain()
'''
