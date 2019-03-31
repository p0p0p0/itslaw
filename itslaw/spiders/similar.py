# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode, urlparse

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem
from redis import Redis, ConnectionPool
from scrapy.conf import settings


class SimilarSpider(scrapy.Spider):
    name = 'similar'
    allowed_domains = ['www.itslaw.com']

    def __init__(self):
        self.pool = ConnectionPool(host=settings["REDIS_HOST"], port=settings["REDIS_PORT"], decode_responses=True, db=0)
        self.r = Redis(connection_pool=self.pool)
    
    def start_requests(self):
        for _ in range(100000):
            doc = self.r.srandmember("itslaw:id")
            for i in range(1, 4):
                parameters = {"type": i}
                url = f"https://www.itslaw.com/api/v1/judgements/judgement/{doc}/courtSimilarJudgements?" + urlencode(parameters)
                yield Request(url=url, meta={"parameters": parameters})

    def parse(self, response):

        res = json.loads(response.body_as_unicode())
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            print(message, error_essage)
            raise CloseSpider(message)
        
        data = res["data"]
        judgements = data['judgements']

        if not judgements:
            return

        for j in judgements:
            yield JudgementItem(id=j["id"])
