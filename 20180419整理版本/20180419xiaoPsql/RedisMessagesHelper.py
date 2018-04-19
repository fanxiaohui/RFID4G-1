# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 14:37:22 2018

@author: root
"""

import redis

class RedisMessagesHelper(object):
    def __init__(self,host='127.0.0.1',psw='123456',port=6379,pool=None,channel='test'):
        self.host=host
        self.psw=psw
        self.port=port
        self.pool=pool
        self.istrue=1
        try:
            if pool!=None:
                self.__conn=redis.Redis(connection_pool=self.pool)
            else:
                self.__conn = redis.Redis(host=self.host,password=self.psw,port=self.port)
                
            if self.__conn.ping():
                print('conn ok')
            else:
                print('shawanyi')
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            self.istrue=0
            return None
            
        self.chan_sub = channel
        self.chan_pub= channel

#发送消息
    def public(self,msg,channel=None):
        if not self.istrue:
            return False
        try:    
            if self.__conn.ping():
                print('conn ok')
        except :
            self.istrue=0
            return False
            
        if channel==None:
            self.__conn.publish(self.chan_pub,msg)
        else:
            self.__conn.publish(channel,msg)
        return True
#订阅
    def subscribe(self,channel=None):
        if not self.istrue:
            return None
        try:    
            if self.__conn.ping():
                print('conn ok')
        except :
            self.istrue=0
            return None
        #打开收音机
        pub = self.__conn.pubsub()
        #调频道
        if channel==None:
            pub.subscribe(self.chan_sub)
        #
        else:
            if isinstance(channel,list):
                pub.psubscribe(channel)  # 同时订阅多个频道，要用psubscribe
            else:
                pub.subscribe(channel)
        #准备接收
        pub.parse_response()
        return pub
        
        
def RunMain():
    '''订阅方'''

#import redis

#from  RedisMessagesHelper import RedisMessagesHelper
#    usepool = redis.ConnectionPool(host='127.0.0.1',password='123456',port=6379)
#    obj = RedisMessagesHelper(pool=usepool)
    obj = RedisMessagesHelper(host='127.0.0.1',psw='123456',port=6379)
    if not obj.istrue:
        return
    redis_sub = obj.subscribe(['test','test1','test2'])

    while True:
        msg = redis_sub.parse_response()
        if len(msg)>0:
            print('接收：',msg)
        
def RunMain1():
    '''发布者'''
#import redis
#from  RedisMessagesHelper import RedisMessagesHelper
#    usepool = redis.ConnectionPool(host='127.0.0.1',password='123456',port=6379)
#    obj = RedisMessagesHelper(pool=usepool)
    obj = RedisMessagesHelper(host='127.0.0.1',psw='123456',port=6379)
    if not obj.istrue:
        return
    obj.public('how are you?',channel='test')

if __name__ == '__main__':
    RunMain()
