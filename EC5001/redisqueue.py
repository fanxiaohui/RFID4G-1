# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:46:37 2018

@author: root
"""
#class redis.StrictRedis(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, unix_socket_path=None)
# 默认redis入库编码是utf-8，如果要修改的话，需要指明 charset 和 decode_responsers 为True. 下面是GBK编码。
#class  redis.StrictRedis (host='localhost', port=6379, db=0, password=None, socket_timeout=None,connection_pool=None,  charset='GBK ' , errors='strict',  decode_responses=True)

import redis
class RedisQueue(object):
    def __init__(self,name,namespace='queue',host='127.0.0.1',psw='123456',port=6379,pool=None,db=1):
    #def __init__(self, name, namespace='queue', **redis_kwargs):
       # redis的默认参数为：host='localhost', port=6379, db=0， 其中db为定义redis database的数量
       #self.__db= redis.Redis(**redis_kwargs)
        self.key = '%s:%s' %(namespace, name)
        self.host=host
        self.psw=psw
        self.port=port
        self.pool=pool
        self.db=db
        self.istrue=1
        
        try:
            if pool!=None:
                self.__conn=redis.Redis(connection_pool=self.pool)
            else:

                self.__conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            print('conn')
            if self.__conn.ping():
                print('conn ok')
            else:
                print('shawanyi')
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            self.istrue=0
            return None
        
    def qsize(self):
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        return self.__conn.llen(self.key)  # 返回队列里面list内元素的数量
    
    def qsize_extend(self,key):
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        return self.__conn.llen(key)  # 返回队列里面list内元素的数量

    def put(self, item):
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        self.__conn.rpush(self.key, item)  # 添加新元素到队列最右方
        print(item)
        print(self.key)

    def put_extend(self, key, item):
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        self.__conn.rpush(key, item)  # 添加新元素到队列最右方

    def get_wait(self, timeout=None):
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__conn.blpop(self.key, timeout=timeout)
        # if item:
        #     item = item[1]  # 返回值为一个tuple
        return item

    def get_wait_extend(self, key, timeout=None):
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__conn.blpop(key, timeout=timeout)
        # if item:
        #     item = item[1]  # 返回值为一个tuple
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        item = self.__conn.lpop(self.key)  
        return item

    def get_nowait_extend(self, key):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        try:
            if self.__conn.ping():
                pass
        except :
            self.istrue=0
            return None
        item = self.__conn.lpop(key)  
        return item
        

import time        
def RunMain():
    #from redisqueue import RedisQueue
    q = RedisQueue('rq')
    if not q.istrue:
        return
    while 1:
        result = q.get_nowait()
#        if not result:
#            break
        print ("output.py: data {} out of queue {}".format(result, time.strftime("%c")))
        time.sleep(2)        
    
def RunMain1():
    #from redisqueue import RedisQueue
    q = RedisQueue('rq')  # 新建队列名为rq
    if not q.istrue:
        return
    for i in range(5):
        q.put(i)
        print ("input.py: data {} enqueue {}".format(i, time.strftime("%c")))
        time.sleep(1)
        
if __name__ == '__main__':
    #RunMain()
    q = RedisQueue('RfidControl')  # 新建队列名为rq
    if not q.istrue:
        pass
    else:
        q.put('Rfidstart')
    time.sleep(2)
    result = q.get_nowait_extend('RfidControl')
   # result = q.get_nowait_extend('RfidControlAnswer')
    print(result)
    
