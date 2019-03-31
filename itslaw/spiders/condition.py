# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode, urlparse, unquote
from time import sleep
from pathlib import Path

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem
from redis import Redis, ConnectionPool
from scrapy.conf import settings


class ConditionSpider(scrapy.Spider):
    name = 'condition'
    allowed_domains = ['www.itslaw.com']
    custom_settings = {
        # "LOG_LEVEL": "DEBUG", 
        "DOWNLOAD_TIMEOUT": 10,
        # "DOWNLOADER_MIDDLEWARES":{
        #     "itslaw.middlewares.ItslawDownloaderMiddleware":200,
        #     }
        }

    def __init__(self):
        self.pool = ConnectionPool(host=settings["REDIS_HOST"], port=settings["REDIS_PORT"], decode_responses=True, db=0)
        self.r = Redis(connection_pool=self.pool)
    
    def start_requests(self):
        with Path("docs/write.txt").open(mode="r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if i > 2000:
                    print("[*] all url loaded")
                    break
                if i <= 1100:
                    continue
                if not line.strip():
                    break
                count, url = line.strip().split()

                for j in range(0, int(count)+1, 20):
                    if j == 1000:
                        break
                    u = url.replace("startIndex=0", f"startIndex={j}")
                    yield Request(url=u, dont_filter=True)
                    print(f"[+] loading {u}")
        
        # while True:
        #     url = self.r.spop("itslaw:error")
        #     if not url:
        #         break
        #     yield Request(url=f"{url}")

    def parse(self, response):
        res = json.loads(response.body_as_unicode())       
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            print(message, error_essage)
            self.r.sadd("itslaw:error", response.url)   

        try:
            data = res["data"]
        except Exception:
            self.r.sadd("itslaw:error", response.url)
            yield Request(url=response.url, dont_filter=True)
            return

        searchResult = data["searchResult"]
        judgements = searchResult["judgements"]

        for each in judgements:
            jid = each["id"]
            yield JudgementItem(id=jid)
        
