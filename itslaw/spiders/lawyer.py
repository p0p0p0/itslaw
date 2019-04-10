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


class LawyerSpider(scrapy.Spider):
    name = 'lawyer'
    allowed_domains = ['app.itslaw.com']
    custom_settings = {
        # "LOG_LEVEL": "DEBUG",
        "DOWNLOAD_TIMEOUT": 5,
        # "DOWNLOAD_DELAY": 0.2,
        "DOWNLOADER_MIDDLEWARES": {
            # "itslaw.middlewares.ProxyMiddleware": 543,
            "itslaw.middlewares.ItslawDownloaderMiddleware": 534
        },
        # "DEFAULT_REQUEST_HEADERS": {
        #     "Host": "app.itslaw.com",
        #     "Cookie": "JSESSIONID=53DE43DD673B3A14EB06599FC420C6C4",
        #     "DeviceId": "NPJEGCQR2RFEZAM2EIIJCZ46LU",
        #     "UA": "iOS_10.3.2-375*667",
        #     "Connection": "keep-alive",
        #     "Accept": "*/*",
        #     "Accept-Language": "zh-cn",
        #     "User-Agent": "WuSong-iOS/7 CFNetwork/811.5.4 Darwin/16.6.0",
        #     "Accept-Encoding": "gzip, deflate",
        #     "App-Version": "9.1.0",
        # },
        "DEFAULT_REQUEST_HEADERS": {
            "Host": "app.itslaw.com",
            "App-Version": "9.1.0",
            "Hanukkah-UserId": "e26ec5dc-0958-4696-b6c7-69a55786d1c9",
            "WuSong-UserId": "e26ec5dc-0958-4696-b6c7-69a55786d1c9",
            "Victory-UserId": "e26ec5dc-0958-4696-b6c7-69a55786d1c9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-cn",
            "token": "e26ec5dc-0958-4696-b6c7-69a55786d1c9",
            "Accept": "*/*",
            "DeviceId": "NPJEGCQR2RFEZAM2EIIJCZ46LU",
            "User-Agent": "WuSong-iOS/7 CFNetwork/811.5.4 Darwin/16.6.0",
            "Connection": "keep-alive",
            "UA": "iOS_10.3.2-375*667",
            "Cookie": "JSESSIONID=DD11AEA57E06C9DA7C3DD37C4F083DBF",
        }
        # "ITEM_PIPELINES": {
        #     'itslaw.pipelines.CasePipeline': 300,
        # }
    }

    def start_requests(self):
        url = "https://app.itslaw.com/app/users/user/e26ec5dc-0958-4696-b6c7-69a55786d1c9/detail?"
        yield Request(url =url)

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        print(res)
        # code = res["result"]["code"]
        # message = res["result"]["message"]
        # self.logger.debug(message)

        # if 0 != code:
        #     error_essage = res["result"]["errorMessage"]
        #     self.logger.debug(error_essage)
        #     # self.r.sadd("conditions:error", response.url)   
        #     return
        # try:
        #     data = res["data"]
        # except Exception as e:
        #     # self.r.sadd("conditions:error", response.url)
        #     self.logger.debug(e)
        #     yield Request(url=response.url, dont_filter=True)
        #     return

        # searchResult = data["searchResult"]
        # judgements = searchResult["judgements"]

        # for each in judgements:
        #     jid = each["id"]
        #     yield JudgementItem(id=jid)
        # else:
        #     # self.r.sadd("conditions:crawled", url)
        #     pass
