import re
import json
from urllib.parse import urlencode
from time import sleep
import logging

from requests import Session

logger = logging.getLogger(__name__)
logger.addFilter(logging.Filter(name=__name__))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(filename)s] %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

url = "https://www.itslaw.com/api/v1/subSites?subSiteCode=bj"
base_url = "https://www.itslaw.com/api/v1/caseFiles?"
patten = re.compile("(\d+)号")

headers = {
    "Host": "www.itslaw.com", 
    "Connection": "keep-alive", 
    "Cache-Control": "no-cache", 
    "Accept": "application/json, text/plain, */*", 
    "Pragma": "no-cache", 
    "DNT": "1", 
    "If-Modified-Since": "Mon, 26 Jul 1997 05:00:00 GMT", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36", 
    "Referer": "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B1994%2B7%2B1994", 
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7", 
    "Cookie": "_t=f239972c-ab49-4087-ada5-98f41526c9de; subSiteCode=bj; showSubSiteTip=false; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1552031585; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1552031585; hideReportMaterialTip=true; _u=b84fe7a6-34f4-4fd7-a94b-52f2cbf380f8; _i=91afad05-3d5b-4b8e-8d96-b5e4f4a5c1c6; _p=2774e9c9-b0a2-4add-bb35-c4172239354c; sessionId=c91acebf-61db-4c45-9712-d6ab07017b16; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1552834998; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1552834998", 
}

def get_case_number(url):
    while True:
        try:
            res = s.get(url, headers=headers)
        except Exception as e:
            # logger.info(e)
            continue
        else:
            try:
                res = res.json()
            except Exception as e:
                logger.info(e)
                logger.info(res)
                continue           
            code = res["result"]["code"]
            message = res["result"]["message"]
            
            if 0 != code:
                error_essage = res["result"]["errorMessage"]
                # print(message, error_essage, res)
                continue
            data = res["data"]
            
            searchResult = data["searchResult"]
            totalCount = searchResult["totalCount"]
            if 0 == totalCount:
                return
            judgements = searchResult["judgements"]
            numbers = set()
            for each in judgements:
                case_number = each.get("caseNumber", "")
                numbers.add(case_number)
            else:
                with open("case_numbers.txt", mode="a", encoding="utf-8") as f:
                    f.write(", ".join(list(numbers)) + "\n")
                return
         


if __name__ == "__main__":
    s = Session()
    with open("urls.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            count, url = line.strip().split()
            get_case_number(url)

