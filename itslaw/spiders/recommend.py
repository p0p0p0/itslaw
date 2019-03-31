# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem


class HomepageRecommendSpider(scrapy.Spider):
    name = 'recommend'
    allowed_domains = ['www.itslaw.com']
    base_url ="https://www.itslaw.com/api/v1/subSites/recommendedJudgements?"
    custom_settings = {"LOG_LEVEL": "DEBUG"}

    def start_requests(self):
        pageSize = 200
        pageNo = 1
        parameters = {
            "pageSize": pageSize,
            "pageNo": pageNo,
        }
        url = self.base_url + urlencode(parameters)
        yield Request(url=url, meta={"parameters": parameters})

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            print(message, error_essage, res)
            raise CloseSpider(message)
        
        data = res["data"]
        # print(data)
        recommendedJudgementInfo = data['recommendedJudgementInfo']
        pageNo = recommendedJudgementInfo["pageNo"]
        recommendedJudgements = recommendedJudgementInfo["recommendedJudgements"]
        print(len(recommendedJudgements))
        for j in recommendedJudgements:
            with open("tmp.txt", mode="a", encoding="utf-8") as f:
                f.write(j["id"]+"\n")
            # print(j["id"])
            # yield JudgementItem(id=j["id"])

        parameters = response.meta["parameters"]
        parameters["pageNo"] = parameters["pageNo"] + 1
        url = self.base_url + urlencode(parameters)

        yield Request(url=url,  meta={"parameters": parameters})
