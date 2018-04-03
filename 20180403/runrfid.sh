#!/bin/bash
cd /opt/redis-4.0.6/src/
sudo ./redis-server /opt/redis-4.0.6/src/redis.conf 
sleep 6
cd /opt/20180306/
sudo python3 /opt/20180306/RfidReadAndWrite-Psql.py
