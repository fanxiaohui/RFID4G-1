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
from redisqueue import RedisQueue
import psycopg2


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
        q = RedisQueue(name=sqstr)
        #q.redisidrun=q.isrun()
        #print ('running')
        while True:
            try:
                data = self.request.recv(1024)
                if(data==b''):
                    try:
                        conn = psycopg2.connect(database="materiel", user="pms", password="pms@pg123", host="58.214.232.165", port="5432")
                        cur = conn.cursor()
                        print('lin postgresql OK')

                    except:
                        print('InsertToPostgresql Connect Fail')
                        break
                    #ProssData(q)
                    while True:
                        if q.isrun() == 0:
                            break
                        qdata=q.get_nowait()

                        if qdata == None:
                            try:
                                conn.commit()
                                conn.close()
                                print('InsertToPostgresql close')
                                break
                            except:
                                print('InsertToPostgresql commit Fail')
                                break

                            #break
                        print(qdata)
                        if b'DEVID' in qdata:
                            devid, value=qdata.split(b':')
                            print('did:{0}'.format(devid))
                            lisoo=value.split(b';')
                            print('did:{0}-epc:{1}'.format(lisoo[0],lisoo[1]))
                            sqlselectstr = ("INSERT INTO tb_epc_record (device_id,epc,report_time) VALUES ('{0}','{1}',NOW()::timestamp)").format(lisoo[0].decode(encoding='utf-8'),lisoo[1].decode(encoding='utf-8'))
                            print(sqlselectstr)
                            cur.execute(sqlselectstr)
                    break#continue
                #print (data)
                q.put(data)
                #if data == b'exit':
                #    print ('exit')
                #    self.server.shutdown()
                #    self.request.close()
                #    break

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
    rt = BigRfidServer()
    rt.BigRfidServerRun()

if __name__ == '__main__':
    RunMain()
