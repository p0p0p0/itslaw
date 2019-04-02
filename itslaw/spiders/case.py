# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from time import time
import base64
import random

import scrapy
from scrapy import Request
# from scrapy.conf import settings
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem, CaseItem
from redis import Redis, ConnectionPool
from fake_useragent import UserAgent
ua = UserAgent()

class CaseSpider(scrapy.Spider):
    name = 'case'
    allowed_domains = ['www.itslaw.com']
    base_url ="https://www.itslaw.com/api/v1/detail?" 
    custom_settings = {
        # "LOG_LEVEL": "DEBUG",
        "DOWNLOAD_TIMEOUT": 5,
        # "DOWNLOAD_DELAY": 0.5,
        "DOWNLOADER_MIDDLEWARES": {
            'itslaw.middlewares.ProxyMiddleware': 543,
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": ua.random, 
            "Referer": "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B1994%2B7%2B1994", 
        },
        "ITEM_PIPELINES": {
            'itslaw.pipelines.CasePipeline': 300,
        }
    }
    settings = get_project_settings()
    redis_host = settings.get("REDIS_HOST")
    redis_port = settings.get("REDIS_PORT")
    redis_key = settings.get("REDIS_KEY")
    max_score = settings.get("MAX_SCORE")
    init_score = settings.get("INIT_SCORE")
    pool = ConnectionPool(host=redis_host, port=redis_port, db=0)
    r = Redis(connection_pool=pool)

    def start_requests(self):
        while True:
            proxies = self.r.zrangebyscore(self.redis_key, self.init_score+1, self.max_score, start=0, num=100)
            if not proxies:
                break
            proxy = str(random.choice(proxies), encoding="utf-8")
            proxy = f"http://{proxy}"
            doc = self.r.srandmember("itslaw:id")
            if self.r.sismember("itslaw:crawled", doc) or self.r.sismember("itslaw:jid", doc):
                continue
            timestamp = str(int(time()*1000))
            judgementId = str(doc, encoding="utf-8")
            
            parameters = {
                "timestamp": timestamp,
                "judgementId": judgementId,
            }
            url = self.base_url + urlencode(parameters)
            yield Request(url=url, meta={"proxy": proxy})

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            print(message, error_essage, res)
            return
        
        data = res["data"]
        fullJudgement = data["fullJudgement"]
        yield CaseItem(item=fullJudgement)
