# -*- codinng: utf-8 -*-


import sys
import threading
import datetime
import Com4GModularClass
import time

def send4gvoid():
    data = b'1234567890'
    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4')
    state = rt4g.Get4GmodeStartFlg()
    state = rt4g.Get4GmodeStartFlg()
    if 'OK' in state:
        print(rt4g.GetStatus())
        # print(rt.StartTcpUseSockA())
        state = rt4g.Senddatasfornet(data)
        print(state)
    time.sleep(2)
    print(rt4g.SetEnableSockA(mode=1, status='OFF'))
    time.sleep(5)
    print(rt4g.StartTcpUseSockA())
    state = rt4g.Senddatasfornet(data)
    print(state)
    print('end')
    time.sleep(5)
    print(rt4g.SetEnableSockA(mode=1, status='OFF'))

    while True:
        time.sleep(1)


def RunMain():
    threading_send=threading.Thread(target=send4gvoid,name='send4gvoid')
    threading_send.setDaemon(False)
    threading_send.start()

if __name__ == '__main__':
    RunMain()