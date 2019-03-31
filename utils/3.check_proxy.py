import requests
from redis import Redis
from urllib.parse import urlencode
from time import time

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
    "Cookie": "_t=f239972c-ab49-4087-ada5-98f41526c9de; showSubSiteTip=false; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1552031585; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1552031585; hideReportMaterialTip=true; subSiteCode=js; sessionId=eacaca54-bf45-447b-b9b9-1104874d41d1; _u=b84fe7a6-34f4-4fd7-a94b-52f2cbf380f8; _i=0b0d4692-97da-4419-93b6-5aac98f5f836; _p=05d4b558-7a74-435c-b375-67f623a4e745; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1553594521; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1553594521", 
}

r = Redis()
s = requests.Session()
base_url = "https://www.itslaw.com/api/v1/detail?"

def check(proxy):
    doc = r.srandmember("itslaw:id")
    jid = str(doc, encoding="utf-8")
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    timestamp = str(int(time()*1000))
    parameters = {
                "timestamp": timestamp,
                "judgementId": jid,
            }
    url = base_url + urlencode(parameters)

    for i in range(5):
        try:
            res = s.get(url, headers=headers, proxies=proxies, timeout=2)
            print(f"[+] {i} test: {proxy}")
        except Exception:
            print(f"[{i}] {proxy} time out")
            break
        else:
            try:
                rid = res.json()["data"]["fullJudgement"]["id"]
            except Exception:
                print(f"[{i}] {proxy} failed")
                break
            else:
                if jid == rid:
                    print(f"[{i}] {proxy} alive")
                    continue
    else:
        return True    
    

if __name__ == "__main__":
    for i in range(1000):
        proxy = r.spop("proxy:good")
        if not proxy:
            break
        proxy = str(proxy, encoding="utf-8")
        if r.sismember("proxy:alive", proxy):
            continue
        print(f"[+] check: {proxy}")
        flag = check(proxy)
        if flag:
            r.sadd("proxy:alive", proxy)
            print(f"[!] Good: {proxy}")
