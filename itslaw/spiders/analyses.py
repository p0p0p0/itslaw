# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from time import sleep

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem


class AnalysesSpider(scrapy.Spider):
    name = 'analyses'
    allowed_domains = ['www.itslaw.com']
    base_url ="https://www.itslaw.com/api/v1/subSites/recommendedCaseAnalyses?"
    custom_settings = {"LOG_LEVEL": "DEBUG"}

    def start_requests(self):
        index = 0
        freeIndex = 0
        pageNo = 1

        parameters = {
            "index": index,
            "freeIndex": freeIndex,
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
        index = data["index"]
        freeIndex = data["freeIndex"]

        caseAnalyses = data["caseAnalyses"]
        for j in caseAnalyses:
            if not j.get("judgementId", None):
                continue
            with open("tmp.txt", mode="a", encoding="utf-8") as f:
                f.write(j["judgementId"]+"\n")
            # print(j["judgementId"])
            # yield JudgementItem(id=j["judgementId"])

        parameters = response.meta["parameters"]
        parameters["pageNo"] = parameters["pageNo"] + 1
        parameters["freeIndex"] = freeIndex
        parameters["index"] = index
        url = self.base_url + urlencode(parameters)

        yield Request(url=url,  meta={"parameters": parameters})
