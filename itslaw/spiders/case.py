# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from time import time
import base64

import scrapy
from scrapy import Request
# from scrapy.conf import settings
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem
from redis import Redis
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
    }
    settings = get_project_settings()
    proxy_pool = settings.get("PROXY_POOL")
    proxy_save = settings.get("PROXY_SAVE")
    redis_host = settings.get("REDIS_HOST")
    redis_port = settings.get("REDIS_PORT")
    r = Redis(host=redis_host, port=redis_port)

    def start_requests(self):
        print(self.redis_host, self.redis_port)
        return
        for _ in range(50000):
            proxy = self.r.spop(f"proxy:{self.proxy_pool}")
            proxy = str(proxy, encoding="utf-8")
            host, port = proxy.split(":")
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
            # auth = "Basic " + base64.urlsafe_b64encode(bytes(("H1Y61OO5H85W1EXD" + ":" + "5BF54645231283E0"), "ascii")).decode("utf8")
            # headers = {
            #         "Proxy-Authorization": auth,
            #     }
            # yield Request(url=url, 
            #             meta={"proxy": "http://http-dyn.abuyun.com:9020"},
            #             headers=headers
            #             )

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
        jid = fullJudgement["id"]
        self.r.sadd("itslaw:jid", jid)
        self.r.sadd("itslaw:judgement", json.dumps(fullJudgement, ensure_ascii=False))
        self.logger.debug(f"[+] {jid} scraped")
