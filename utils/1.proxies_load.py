#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "Sigai"
import re
from pathlib import Path
import random
from time import sleep
from datetime import datetime

from redis import Redis
import requests
from scrapy.selector import Selector

r = Redis()

def load_from_file():
    proxies = set()
    with Path("../docs/proxies.txt").open(mode="r" , encoding="utf-8") as f:
        for line in f:
            proxies.add(line.strip())

    for proxy in proxies:
        r.zadd("proxy:rank", {proxy: 3})

    print(f"[+] total {len(proxies)} hosts")


def load_from_66ip():
    pattern = r"\d+\.\d+.\d+\.\d+:\d+"
    url = "http://www.66ip.cn/nmtq.php?getnum=100&area=1&proxytype=2&isp=1&anonymoustype=4"
    res = requests.get(url)
    for proxy in re.findall(pattern, str(res.content, encoding="gbk")):
        r.zadd("proxy:rank", {proxy: 3})


def load_from_xici():
    for i in range(1):
        url = f"https://www.xicidaili.com/wt/{i+1}"
        print(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3745.4 Safari/537.36",
            "Referer": "https://www.xicidaili.com/wt/"
        }
        while True:
            try:
                res = requests.get(url, headers=headers)
            except Exception as e:
                print(e)
            else:
                if res.status_code == 200:
                    break
                else:
                    sleep(1)
        response = Selector(text=str(res.content, encoding="utf-8"))
        rows = response.xpath("//tr")
        for row in rows[1:]:
            ip = row.xpath(".//td[2]/text()").extract_first()
            port = row.xpath(".//td[3]/text()").extract_first()
            r.zadd("proxy:rank", {f"{ip}:{port}": 3})


def load_from_kuaidaili():
    for i in range(10):
        url = f"https://www.kuaidaili.com/free/inha/{i+1}/"
        print(url)
        while True:
            try:
                res = requests.get(url)
            except Exception as e:
                print(e)
            else:
                if res.status_code == 200:
                    break
                else:
                    sleep(1)
        response = Selector(text=str(res.content, encoding="utf-8"))
        rows = response.xpath("//tbody/tr")
        for row in rows:
            ip = row.xpath(".//td[@data-title='IP']/text()").extract_first()
            port = row.xpath(".//td[@data-title='PORT']/text()").extract_first()
            r.zadd("proxy:rank", {f"{ip}:{port}": 3})


def load_from_5u():
    url = "http://www.data5u.com/"
    print(url)
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3745.4 Safari/537.36",
            "Referer": "http://www.data5u.com/"
        }
    while True:
        try:
            res = requests.get(url, headers=headers)
        except Exception as e:
            print(e)
        else:
            if res.status_code == 200:
                break
            else:
                sleep(1)
    response = Selector(text=str(res.content, encoding="utf-8"))
    rows = response.xpath('//ul[contains(@class, "l2")]')
    for row in rows:
        ip = row.xpath(".//span[1]/li/text()").extract_first()
        port = row.xpath(".//span[2]/li/text()").extract_first()
        r.zadd("proxy:rank", {f"{ip}:{port}": 3})


def load_from_iphai():
    items = ["ng", "np"]
    for each in items:
        url = f"http://www.iphai.com/free/{each}"
        print(url)
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3745.4 Safari/537.36",
                "Referer": "http://www.data5u.com/"
            }
        while True:
            try:
                res = requests.get(url, headers=headers)
            except Exception as e:
                print(e)
            else:
                if res.status_code == 200:
                    break
                else:
                    sleep(1)
        response = Selector(text=str(res.content, encoding="utf-8"))
        rows = response.xpath('//tr')
        for row in rows[1:]:
            ip = row.xpath(".//td[1]/text()").extract_first().strip()
            port = row.xpath(".//td[2]/text()").extract_first().strip()
            r.zadd("proxy:rank", {f"{ip}:{port}": 3})


def load_from_redis():
    while True:
        proxy = r.spop("proxy:great")
        if not proxy:
            break
        r.zadd("proxy:rank", {str(proxy, encoding="utf-8"): 5})

def get_proxy():
    res = r.zrangebyscore("proxy:rank", 5, 10, start=0, num=100)

    print(random.choice(res))

def increase_score():
    res = r.zincrby("proxy:rank", 1, "1.10.186.167:51907")
    print(res)

def reduce_score():
    res = r.zincrby("proxy:rank", -1, "1.10.186.167:51907")
    print(res)

def count():
    ret = 0
    print(f"{datetime.now().isoformat(timespec='seconds')} |", end="")
    for i in range(1, 6):
        res = r.zcount("proxy:rank", i, i)
        print(f"{i}♥: {res:4}", end="|")
        if i == 3:
            ret=res
    print()
    return ret


def remove_disqualified():
    res = r.zremrangebyscore("proxy:rank", 0, 1)


def init():
    res = r.zrangebyscore("proxy:rank", 0, -1, withscores=True)
    for proxy, score in res:
        r.zincrby("proxy:rank", 3-score, proxy)

if __name__ == "__main__":
    funcs = [load_from_66ip, load_from_xici, load_from_kuaidaili, load_from_5u, load_from_iphai]
    while True:
        for i in range(5):
            remove_disqualified()
            c = count()
            if c < 10:
                for func in funcs[:1]:
                    func()
            sleep(60)
        for func in funcs[:1]:
            func()

    # load_from_file()
    # remove_disqualified()


