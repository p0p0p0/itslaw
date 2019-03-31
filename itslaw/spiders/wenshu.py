# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from itslaw.items import JudgementItem


class WenshuSpider(scrapy.Spider):
    name = 'wenshu'
    allowed_domains = ['itslaw.com']
    base_url = "https://www.itslaw.com/api/v1/caseFiles?"
    cookies = {"_t": "f239972c-ab49-4087-ada5-98f41526c9de", 
                "subSiteCode": "bj", 
                "showSubSiteTip": "false", 
                "sessionId": "440fe872-4dd3-423c-9418-8c93871f648c", 
                "_u": "b84fe7a6-34f4-4fd7-a94b-52f2cbf380f8", 
                "_i": "ca3acdd6-1d1e-4f32-a34a-64b99d48f5d5", 
                "_p": "57a4e8be-e96d-4f05-8789-3742e8dc211c",
}
    year = 1997
    def start_requests(self):
        start = 0
        trial_year = self.year
        conditions = f"trialYear+{trial_year}+7+{trial_year}"
        parameters = {
            "startIndex": start*20,
            "countPerPage": 20,
            "sortType": 1,
            "conditions": conditions
        }
        url = self.base_url + urlencode(parameters)
        yield Request(url=url, cookies=self.cookies, meta={"parameters": parameters})

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        code = res["result"]["code"]
        message = res["result"]["message"]
        
        if 0 != code:
            error_essage = res["result"]["errorMessage"]
            print(message, error_essage)
            raise CloseSpider(message)

        data = res["data"]
        search_result = data["searchResult"]
        total_count = search_result['totalCount']
        if total_count > 400:
            raise CloseSpider(response.url)
        else:
            # print(search_result)
            
            for judgement in search_result["judgements"]:
                item = JudgementItem(json=json.dumps(judgement, indent=4, ensure_ascii=False))
                # item["caseNumber"] = judgement["caseNumber"]
                # item["caseType"] = judgement["caseType"]
                # item["courtName"] = judgement["courtName"]
                # item["courtOpinion"] = judgement["courtOpinion"]
                # item["hasCaseAnalysis"] = judgement["hasCaseAnalysis"]
                # item["hasHistoricalJudgment"] = judgement["hasHistoricalJudgment"]
                # item["hasWusongReaderActicle"] = judgement["hasWusongReaderActicle"]
                # item["id"] = judgement["id"]
                # item["judgementDate"] = judgement["judgementDate"]
                # item["judgementType"] = judgement["judgementType"]
                # item["keywords"] = judgement["keywords"]
                # item["publishDate"] = judgement["publishDate"]
                # item["publishType"] = judgement["publishType"]
                # item["similarJudgement"] = judgement["similarJudgement"]
                # item["temporarySearchReport"] = judgement["temporarySearchReport"]
                # item["tiantongCode"] = judgement["tiantongCode"]
                # item["title"] = judgement["title"]
                # item["trialRound"] = judgement["trialRound"]
                # item["watched"] = judgement["watched"]

                yield item
            else:
                if len(search_result["judgements"]) < 20:
                    return
                parameters = response.meta["parameters"]
                parameters["startIndex"] += 20
                url = self.base_url + urlencode(parameters)

                yield Request(url=url, cookies=self.cookies, meta={"parameters": parameters})
