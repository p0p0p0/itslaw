# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode, urlparse, unquote
from time import sleep
import base64
from pathlib import Path

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
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36", 
            "Referer": "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B1994%2B7%2B1994", 
        },
        "ITEM_PIPELINES": {
            'itslaw.pipelines.ItslawPipeline': 300,
        }
    }
    settings = get_project_settings()
    redis_host = settings.get("REDIS_HOST")
    redis_port = settings.get("REDIS_PORT")
    proxy_server = settings.get("PROXY_SERVER")
    proxy_user = "H558RH6N14I4K13D"
    proxy_pass = "FD8741C99A72B6C1"
    proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user + ":" + proxy_pass), "ascii")).decode("utf8")
    pool = ConnectionPool(host=redis_host, port=redis_port, db=0)
    r = Redis(connection_pool=pool)
    
    def start_requests(self):
        #         for j in range(0, int(count)+1, 20):
        #             u = url.replace("startIndex=0", f"startIndex={j}")
  
        while True:
            left = self.r.sdiffstore("conditions:count1", "conditions:count1", "conditions:crawled")
            self.logger.info(f"[*] left {left} cases to crawl.")
            urls = self.r.srandmember("conditions:count1", number=20000)
            if not urls:
                break
            for url in urls:
                yield Request(str(url, encoding="utf-8"))

    def parse(self, response):
        url = response.url
        res = json.loads(response.body_as_unicode())       
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            self.logger.debug(message + ": " + error_essage)
            self.r.sadd("conditions:error", response.url)   
            return

        try:
            data = res["data"]
        except Exception as e:
            self.r.sadd("conditions:error", response.url)
            self.logger.debug(e)
            yield Request(url=response.url, dont_filter=True)
            return

        searchResult = data["searchResult"]
        judgements = searchResult["judgements"]

        for each in judgements:
            jid = each["id"]
            yield JudgementItem(id=jid)
        else:
            self.r.sadd("conditions:crawled", url)
