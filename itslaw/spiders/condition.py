# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode, urlparse, unquote
from time import sleep
import base64
from pathlib import Path
import os

import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem
from redis import Redis, ConnectionPool
from scrapy.conf import settings


class ConditionSpider(scrapy.Spider):
    name = 'condition'
    allowed_domains = ['www.itslaw.com']
    custom_settings = {
        # "LOG_LEVEL": "DEBUG",
        "DOWNLOAD_TIMEOUT": 5,
        # "DOWNLOAD_DELAY": 0.2,
        "DOWNLOADER_MIDDLEWARES": {
            'itslaw.middlewares.ProxyMiddleware': 543,
            # "itslaw.middlewares.ItslawDownloaderMiddleware": 534
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36", 
            "Referer": "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B1994%2B7%2B1994",
            "Cookie": "_t=0e9084b2-59b6-4cab-985f-be99b553e944; showSubSiteTip=false; subSiteCode=bj; LXB_REFER=www.wusong.com; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1554601609,1555339418,1555339440,1555339451; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1554601609,1555339418,1555339440,1555339451; sessionId=f3252d05-e43e-4eda-acef-a56d78a3cdb8; _u=dc0413b3-06a9-4fb2-b5e5-24673d73efeb; _i=879d0edc-e45a-4e59-906c-93f076e8d0d6; _p=08204e75-0309-43de-98a9-7c397d0670c5; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1556102661; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1556102661",
        },
        "ITEM_PIPELINES": {
            'itslaw.pipelines.ConditionPipeline': 300,
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
    key = f'condition:more{os.getenv("COUNT", "")}'
    # key = f'conditions:error'
    
    def start_requests(self):
        # $env:COUNT=""
        while True:
            left = self.r.sdiffstore(self.key, self.key, "condition:crawled")
            self.logger.info(f"[*] left {left} condition combinations to crawl.")
            urls = self.r.srandmember(self.key, number=10000)
            if not urls:
                break
            for url in urls:
                yield Request(str(url, encoding="utf-8"), dont_filter=True)

    def parse(self, response):
        url = response.url
        try:
            res = json.loads(response.body_as_unicode())
        except Exception as e:
            return    
        code = res["result"]["code"]
        message = res["result"]["message"]
        self.logger.debug(message)
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            self.logger.debug(error_essage)
            self.r.sadd("condition:error", response.url)   
            return

        try:
            data = res["data"]
        except Exception as e:
            self.r.sadd("condition:error", response.url)
            self.logger.debug(e)
            yield Request(url=response.url, dont_filter=True)
            return

        searchResult = data["searchResult"]
        judgements = searchResult.get("judgements", [])

        for each in judgements:
            jid = each["id"]
            yield JudgementItem(id=jid)
        else:
            self.r.sadd("condition:crawled", url)
