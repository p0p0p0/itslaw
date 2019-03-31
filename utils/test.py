import requests
from redis import Redis
import json
from urllib.parse import urlencode
from time import time
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s [%(filename)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
ua = UserAgent()

headers = {
    # "Host": "www.itslaw.com", 
    # "Connection": "keep-alive", 
    # "Cache-Control": "no-cache", 
    # "Accept": "application/json, text/plain, */*", 
    # "Pragma": "no-cache", 
    # "DNT": "1", 
    # "If-Modified-Since": "Mon, 26 Jul 1997 05:00:00 GMT", 
    "User-Agent": None, 
    "Referer": "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B1994%2B7%2B1994", 
    # "Accept-Encoding": "gzip, deflate, br", 
    # "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7", 
    # "Cookie": "_t=f239972c-ab49-4087-ada5-98f41526c9de; showSubSiteTip=false; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1552031585; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1552031585; hideReportMaterialTip=true; subSiteCode=js; sessionId=78c63bc2-70b7-4f66-a35f-8921ed714094; _u=b84fe7a6-34f4-4fd7-a94b-52f2cbf380f8; _i=abccf6e4-58db-4242-8d1c-5dc8405d904c; _p=1f523b90-4138-4cfc-8878-ec42848e48dd; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1553610995; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1553610995", 
}

base_url = "https://www.itslaw.com/api/v1/detail?"

r = Redis()
s = requests.Session()

for i in range(1):
    headers["User-Agent"] = ua.random
    doc = r.srandmember("itslaw:id")
    jid = str(doc, encoding="utf-8")
    logger.debug(f"jid: {jid}")
    # proxy = r.srandmember("proxy:good")
    # proxy = str(proxy, encoding="utf-8")
    # logger.debug(f"proxy: {proxy}")
    # proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    timestamp = str(int(time()*1000))
    parameters = {
                "timestamp": timestamp,
                "judgementId": jid,
            }
    url = base_url + urlencode(parameters)
    try:
        logger.debug("start...")
        res = s.get(url, headers=headers, proxies=proxies, timeout=60)
        logger.debug("end...")
    except Exception as e:
        print(e)
        pass
    else:
        print(res.json()["data"]["fullJudgement"]["id"])
        # print(res.json())
        

#TODO: test each header, make multi fake users