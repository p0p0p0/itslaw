# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from time import time, sleep
import base64
import random
import os

import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem, CaseItem
from redis import Redis, ConnectionPool


class CaseSpider(scrapy.Spider):
    name = 'case'
    allowed_domains = ['www.itslaw.com']
    # base_url = "https://m.itslaw.com/mobile/judgements/judgement/"
    custom_settings = {
        # "LOG_LEVEL": "DEBUG",
        "DOWNLOAD_TIMEOUT": 5,
        # "DOWNLOAD_DELAY": 0.2,
        "DOWNLOADER_MIDDLEWARES": {
            'itslaw.middlewares.ProxyMiddleware': 543,
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1", 
            "Referer": "https://m.itslaw.com", 
        },
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
                url = f"https://m.itslaw.com/mobile/judgements/judgement/{judgementId}"
                yield Request(url=url)

    def parse(self, response):
        jid = response.url.split("=")[-1]
        res = json.loads(response.body_as_unicode())
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        # save failed id to redis
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            self.r.sadd("itslaw:failed", jid)
            return
        
        data = res["data"]
        fullJudgement = data["fullJudgement"]
        yield CaseItem(item=fullJudgement)
