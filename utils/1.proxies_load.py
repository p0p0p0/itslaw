#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "Sigai"

from pathlib import Path
from redis import Redis

r = Redis()
proxies = set()

with Path("../docs/proxies.txt").open(mode="r" , encoding="utf-8") as f:
    for line in f:
        proxies.add(line.strip())

for proxy in proxies:
    r.sadd("proxy:pool", proxy)

print(f"[+] total {len(proxies)} hosts")
