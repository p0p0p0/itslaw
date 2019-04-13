# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from time import time, sleep
import base64
import random
import os

from fake_useragent import UserAgent
import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem, CaseItem
from redis import Redis, ConnectionPool

ua = UserAgent()

class CaseSpider(scrapy.Spider):
    name = 'case'
    allowed_domains = ['www.itslaw.com']
    base_url = "https://www.itslaw.com/api/v1/detail?"
    custom_settings = {
        # "LOG_LEVEL": "DEBUG",
        "DOWNLOAD_TIMEOUT": 5,
        # "DOWNLOAD_DELAY": 0.2,
        "DOWNLOADER_MIDDLEWARES": {
            "itslaw.middlewares.ProxyMiddleware": 543,
            # "itslaw.middlewares.ItslawDownloaderMiddleware": 534
        },
        "DEFAULT_REQUEST_HEADERS": {
            "Cookie": "_t=0e9084b2-59b6-4cab-985f-be99b553e944; LXB_REFER=mail.qq.com; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1554555977,1554601580,1554601590,1554601609; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1554555977,1554601580,1554601591,1554601609; showSubSiteTip=false; subSiteCode=bj; sessionId=a0fa1674-5ef7-49b7-83c2-b804b2d522b2; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1554817712; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1554817712",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.itslaw.com",
            "If-Modified-Since": "Mon, 26 Jul 1997 05:00:00 GMT",
            "Pragma": "no-cache",
            "User-Agent": ua.random, 
            "Referer": "https://www.itslaw.com/", 
        },
        # "DEFAULT_REQUEST_HEADERS": {
        #     "Accept": "application/json, text/javascript, */*; q=0.01",
        #     "Content-Type": "application/json;charset=utf-8",
        #     "DNT": "1",
        #     "Referer": "https://m.itslaw.com/mobile/",
        #     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
        #     "X-Requested-With": "XMLHttpRequest",
        # },
        "ITEM_PIPELINES": {
            'itslaw.pipelines.CasePipeline': 300,
        }
    }
    settings = get_project_settings()
    redis_host = settings.get("REDIS_HOST")
    redis_port = settings.get("REDIS_PORT")
    proxy_server = settings.get("PROXY_SERVER")
    proxy_user = settings.get("PROXY_USER")
    proxy_pass = settings.get("PROXY_PASS")
    proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user + ":" + proxy_pass), "ascii")).decode("utf8")
    pool = ConnectionPool(host=redis_host, port=redis_port, db=0)
    r = Redis(connection_pool=pool)
    count = os.getenv("COUNT", default="")
    key = f'itslaw:id{count}'
    # $env:COUNT=""

    def start_requests(self):
        while True:
            left = self.r.sdiffstore(self.key, self.key, "itslaw:jid")
            self.logger.info(f"[*] {self.count} left {left} cases to crawl.")
            docs = self.r.srandmember(self.key, number=10000)
            for doc in docs:
                judgementId = str(doc, encoding="utf-8")
                parameters = {
                    "timestamp": int(time()*1000),
                    "judgementId": judgementId,
                }
                url = self.base_url + urlencode(parameters)
                # url = f"https://m.itslaw.com/mobile/judgements/judgement/{judgementId}"
                yield Request(url=url)
            else:
                sleep(60)


    def parse(self, response):
        jid = response.url.split("=")[-1]
        try:
            res = json.loads(response.body_as_unicode())
        except Exception as e:
            return
        code = res["result"]["code"]
        
        # save failed id to redis
        if 0 != code:
            self.r.sadd("itslaw:failed", jid)
            return
        
        data = res["data"]
        fullJudgement = data["fullJudgement"]
        yield CaseItem(item=fullJudgement)
