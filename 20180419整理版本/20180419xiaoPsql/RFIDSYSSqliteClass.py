# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 21:02:58 2018

@author: root
"""

import sqlite3

class RfidSysSqlite3Class(object):
    def __init__(self, db='Rfidsys.db'):
        self.db=db
        self.conn=None
        
    def Sqlite3conndb(self):
        if self.conn!=None:
            return None
        try:
            conn = sqlite3.connect(self.db)
            #print(conn)
            return conn
        except:
            print('conn erro')
            return None

    def Sqlite3Updatedata(self,dict):
        if self.conn==None:
            print('Sqlite3creattabl')
            connn=self.Sqlite3conndb()
            if connn == None:
                print('Sqlite3creattabl False')
                return False
                
        sql = '''UPDATE rfidsystable SET 
            ID = {0},
            gettagsleep = {1},
            senddatasleeptime = {2},
            Ant1 = {3},
            Ant2 = {4},
            Ant3 = {5},
            Ant4 = {6},
            Antpow = {7},
            serverip1 = '{8}',
            serverip2 = '{9}',
            serverip3 = '{10}',
            serverip4 = '{11}'
            WHERE ID == 0
            '''.format(0,dict['ts'],dict['ss'],dict['a1'],dict['a2'],dict['a3'],dict['a4'],dict['aw'],dict['sip1'],dict['sip2'],dict['sip3'],dict['sip4'])
        print(sql)
        
        try:        
            cursor = connn.cursor()
            cursor.execute(sql)
            
            connn.commit()
            cursor.close()
            connn.close()
                        
            return True
        except:
            print('----')
            return False
            
    def Sqlite3Getdata(self):
        if self.conn==None:
            print('Sqlite3creattabl')
            connn=self.Sqlite3conndb()
            if connn == None:
                print('Sqlite3creattabl False')
                return None
        try:        
            cursor = connn.cursor()
            sql = '''SELECT * FROM rfidsystable WHERE ID = 0'''
            #sql = '''SELECT ID,gettagsleep,senddatasleeptime,Ant1,Ant2,Ant3,Ant4,Antpow,serverip1,serverip2,serverip3,serverip4 FROM rfidsystable WHERE ID == 0'''

            cursor.execute(sql)
            
            o = cursor.fetchall()
            #print (len(o))
            cursor.close()
                        
            ret={'ts':0,'ss':0,'a1':1,'a2':2,'a3':3,'a4':4,'aw':0,'sip1':'','sip2':'','sip3':'','sip4':''}
            for v in o:
                print(v)
                ret['ts']=v[1]
                ret['ss']=v[2]
                ret['a1']=v[3]
                ret['a2']=v[4]
                ret['a3']=v[5]
                ret['a4']=v[6]
                ret['aw']=v[7]
                ret['sip1']=v[8]
                ret['sip2']=v[9]
                ret['sip3']=v[10]
                ret['sip4']=v[11]
#            connn.close()
            print (ret)
            return ret
        except:
            print('----')
            return None
        
    def Sqlite3creattabl(self):
        if self.conn==None:
            print('Sqlite3creattabl')
            connn=self.Sqlite3conndb()
            if connn == None:
                print('Sqlite3creattabl False')
                return False
        try:        
            cursor = connn.cursor()
            sql = '''create table rfidsystable (
                ID INT PRIMARY KEY     NOT NULL,
                gettagsleep int,
                senddatasleeptime int,
                Ant1 int,
                Ant2 int,
                Ant3 int,
                Ant4 int,
                Antpow int,
                serverip1 text,
                serverip2 text,
                serverip3 text,
                serverip4 text
                )'''

            cursor.execute(sql)
            connn.commit()
            sqlset = '''INSERT INTO rfidsystable (ID,gettagsleep,senddatasleeptime,Ant1,Ant2,Ant3,Ant4,Antpow,serverip1,serverip2,serverip3,serverip4)
                VALUES (0, 30, 150, 1,0,0,0,3000,"192.168.1.105","","","")
                '''
                
            cursor.execute(sqlset)
            
            connn.commit()
            cursor.close()
            connn.close()
            
            return True
        except:
            print('----')
            return False

def RunMain():
    
    rt=RfidSysSqlite3Class(db='/opt/Test/Rfidsys.db')
    #print(rt.Sqlite3creattabl())
    test=rt.Sqlite3Getdata()
    test['sip2']=''
    test['sip3']=''
    test['sip4']=''
    if rt.Sqlite3Updatedata(test):
        tt=rt.Sqlite3Getdata()
#    if rt.RunAllStart():
#        pass
#    else:
#        pass

if __name__ == '__main__':
    RunMain()
