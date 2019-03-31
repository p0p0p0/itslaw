#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "Sigai"
from redis import Redis
import telnetlib
import time


r = Redis()

def check(proxy, r):
    host, port = str(proxy, encoding="utf-8").split(":")
    print(f"[+] ping {host}:{port}")
    for i in range(5):
        start = time.time()
        try:
            telnetlib.Telnet(host, port=port, timeout=1)
        except Exception as e:
            print(e)
            break
        else: 
            end = time.time()
            if (end - start) < 100:
                print(f"\t[{i+1}]alive!")
                time.sleep(1)
                continue
    else:
        r.sadd("proxy:alive", proxy)
        print(f"\t[+]alive {host}:{port}")


while True:
    proxy = r.spop("proxy:pool")
    if not proxy:
        break
    if r.sismember("proxy:alive", proxy):
        continue
    check(proxy, r)


