# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 12:00:09 2018

@author: root
"""


#!/usr/bin/env python
# coding=utf-8

import sys
import ctypes
from ctypes import *
from socket import *
import socket
import socketserver
#from redisqueue import RedisQueue
#import psycopg2


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


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
        print(self.client_address)
        sqstr='{0}:{1}'.format(self.client_address[0],self.client_address[1])
        print(sqstr)
        #q = RedisQueue(name=sqstr)
        #q.redisidrun=q.isrun()
        #print ('running')
        while True:
            try:
                data = self.request.recv(1024)
                if(data==b''):
                    print('break')
                    break#continue
                print (data)
                epcdata=data.split(b'+')
                for var in epcdata:
                    print(var)
                    
            except Exception as e:
                self.server.shutdown()
                self.request.close()
                break

class BigRfidServer(object):
    def __init__(self, port=9999, host='', maxLinks=10):
        self.port=port
        if host =='':
            self.host=get_host_ip()
            print(self.host)
        else:
            self.host=host
        self.bufsize=1024
        self.maxLinks=maxLinks

    def BigRfidServerRun(self):
        # socketserver的多进程非阻塞启动
        # server = socketserver.ThreadingTCPServer(('localhost',9999),RequestHandler)
        server = socketserver.ThreadingTCPServer((self.host, self.port), RequestHandler)
        server.serve_forever()


def RunMain():
    rt = BigRfidServer(host='127.0.0.1')#rt = BigRfidServer(host='10.10.100.133')
    rt.BigRfidServerRun()

if __name__ == '__main__':
    RunMain()
