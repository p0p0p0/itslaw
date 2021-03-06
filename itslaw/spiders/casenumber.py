# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode, urlparse, unquote
from time import sleep
import base64
from pathlib import Path
import os
import gc

import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem
from redis import Redis, ConnectionPool
from scrapy.conf import settings


class CaseNumberSpider(scrapy.Spider):
    name = 'casenumber'
    allowed_domains = ['www.itslaw.com']
    custom_settings = {
        "LOG_LEVEL": "DEBUG",
        # "DOWNLOAD_TIMEOUT": 5,
        # "DOWNLOAD_DELAY": 0.2,
        "DOWNLOADER_MIDDLEWARES": {
            # 'itslaw.middlewares.ProxyMiddleware': 543,
            "itslaw.middlewares.ItslawDownloaderMiddleware": 534
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36", 
            "Referer": "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B1994%2B7%2B1994",
            # "Cookie": "_t=0e9084b2-59b6-4cab-985f-be99b553e944; sessionId=49f99a6a-99e0-438a-8181-f3757aa8e267; LXB_REFER=mail.qq.com; _u=f0c76f8f-8df1-4e56-832a-7aa5fe6118c4; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1554555977,1554601580,1554601590,1554601609; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1554555977,1554601580,1554601591,1554601609; _i=bf039e9d-6188-4c4a-8bce-b4bd757b6b67; _p=032dd594-483e-4ec8-ab62-773cf754fdb9; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1554601618; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1554601618",
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
    count = os.getenv("COUNT", "")
    key = f'conditions:case{count}'
    # key = f'conditions:error'
    
    def start_requests(self):
        # $env:COUNT=""
        self.name += self.count
        while True:
            self.r.sdiffstore(self.key, self.key, "conditions:crawled")
            self.r.sdiffstore(self.key, self.key, "conditions:pages")
            self.r.sdiffstore(self.key, self.key, "conditions:beyond")
            left = self.r.sdiffstore(self.key, self.key, "conditions:noresult")
            self.logger.info(f"left {left} condition combinations to crawl.")
            urls = self.r.srandmember(self.key, number=10000)
            if not urls:
                break
            for url in urls:
                yield Request(str(url, encoding="utf-8"), dont_filter=True)
            
    def parse(self, response):
        url = response.url
        res = json.loads(response.body_as_unicode())       
        code = res["result"]["code"]
        message = res["result"]["message"]
        self.logger.debug(message)
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            self.logger.debug(error_essage)
            return

        try:
            data = res["data"]
        except Exception as e:
            self.logger.debug(e)
            yield Request(url=response.url, dont_filter=True)
            return

        searchResult = data["searchResult"]
        total_count = searchResult["totalCount"]
        if 0 == total_count:
            self.r.sadd("conditions:noresult", url)
        elif total_count <= 20:
            judgements = searchResult["judgements"]
            for each in judgements:
                jid = each["id"]
                yield JudgementItem(id=jid)
            else:
                self.r.sadd("conditions:crawled", url)
        elif total_count <= 400:
            self.r.sadd("conditions:pages", url)
        else:
            self.r.sadd("conditions:beyond", url)

            
