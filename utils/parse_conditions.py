import json
from urllib.parse import urlencode
from time import sleep
import logging

from requests import Session

["trialYear", "trialRound", "judgementType", "court", "reason"]
logger = logging.getLogger(__name__)
logger.addFilter(logging.Filter(name=__name__))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(filename)s] %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

url = "https://www.itslaw.com/api/v1/subSites?subSiteCode=bj"
base_url = "https://www.itslaw.com/api/v1/caseFiles?"

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


def get_subsites():
    cities = []
    while True:
        try:
            res = s.get(url, headers=headers, timeout=3)
        except Exception as e:
            logger.info(e)
            sleep(1)
        else:
            res = res.json()
            code = res["result"]["code"]
            message = res["result"]["message"]
            
            if 0 != code:
                error_essage = res["result"]["errorMessage"]
                print(message, error_essage, res)
            data = res["data"]
            subSites = data["subSites"]
            logger.debug(len(subSites))
            for each in subSites:
                logger.debug(f'{each["name"]}, {each["code"]}')
                cities.append(each["name"])
            return cities
            break
    

def get_tree(url=base_url):
    read = []
    write = []
    filter = "reason"
    return crawl(url, filter, read, write)     


def crawl(url, filter, read, write):
    # logger.debug(url)
    while True:
        try:
            res = s.get(url, headers=headers, timeout=2)
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
                return read, write
            # 带top开头的都不是过滤条件
            # 裁判年份
            judgementDateResults = searchResult["judgementDateResults"]            
            # 审理程序: 一审, 二审, 再审, 其他
            trialRoundResults = searchResult["trialRoundResults"]
            # 文书性质: 裁决, 裁定, 调解, 通知, 决定
            judgementTypeResults = searchResult["judgementTypeResults"]            
            # 地域: 其实是法院court
            regionResults = searchResult["regionResults"]            
            # 案由
            reasonResults = searchResult["reasonResults"]
            # 关键词:
            keywordResults = searchResult["keywordResults"]
            # 搜索文书结果
            judgements = searchResult["judgements"]
            
            logger.debug(totalCount)

            if "court" == filter:
                code = 5
                for each in regionResults:
                    condition_parser(filter, code, each, read, write)

            elif "reason" == filter:
                code = 4
                for each in reasonResults:
                    condition_parser(filter, code, each, read, write)            


            # "下面的不需要解析, 直接组合"
            elif "trialYear" == filter:
                code = 7
                for each in judgementDateResults:
                    level = each["id"]
                    name = each["name"]
                    count = each["count"]
                    if 400 >= count:
                        read.append((f"{filter}+{level}+{code}+{name}", count))
                    else:
                        write.append((f"{filter}+{level}+{code}+{name}", count))

            elif "trialRound" == filter:
                code = 8
                for each in trialRoundResults:
                    level = each["id"]
                    name = each["name"]
                    count = each["count"]
                    if 400 >= count:
                        read.append((f"{filter}+{level}+{code}+{name}", count))
                    else:
                        write.append((f"{filter}+{level}+{code}+{name}", count))

            elif "judgementType" == filter:
                code = 9
                for each in judgementTypeResults:
                    level = each["id"]
                    name = each["name"]
                    count = each["count"]
                    if 400 >= count:
                        read.append((f"{filter}+{level}+{code}+{name}", count))
                    else:
                        write.append((f"{filter}+{level}+{code}+{name}", count))
            
            for each in judgements:
                with open("judgements.txt", mode="a", encoding="utf-8") as f:
                    f.write(each["id"] + "\n")

            files = []
            folders = []
            for condition, count in read:
                filename = url +"&" + urlencode({"conditions": condition})
                files.append((filename, count))
            for condition, count in write:
                foldername = url +"&" + urlencode({"conditions": condition})
                folders.append((foldername, count))
            return files, folders


def condition_parser(filter, code, each, read, write):
    name, label, level = each["id"].split("::")
    text = each["text"]
    count = text.replace(name, "")[1:-1]
    count = int(count)
    children = each.get("children", None)
    if children:
        for child in children:
            condition_parser(filter, code, child, read, write)
    else:
        if 400 >= count:
            read.append((f"{filter}+{level}+{code}+{name}", count))
        else:
            write.append((f"{filter}+{level}+{code}+{name}", count))


if __name__ == "__main__":
    s = Session()
    # 生成初始链接
    # for i in range(2020, 2017, -1):
    #     url = f"https://www.itslaw.com/api/v1/caseFiles?startIndex=0&countPerPage=20&sortType=1&conditions=trialYear%2B{i}%2B7%2B{i}"
    #     files, folders = get_tree(url=url)
    #     for url, count in files:
    #         with open("read.txt", mode="a", encoding="utf-8") as f:
    #             f.write(f"{count}\t{url}\n")
    #     for url, count in folders:
    #         with open("write.txt", mode="a", encoding="utf-8") as f:
    #             f.write(f"{count}\t{url}\n")
    
    lines = []

    with open("write.txt", mode="r", encoding="utf-8") as w:
        for line in w:
            count, url = line.strip().split()
            lines.append((count, url))
    
    for count, url in lines:
        files, folders = get_tree(url=url)
        logger.debug(len(files))
        logger.debug(len(folders))

        for url, count in files:
            with open("read.txt", mode="a", encoding="utf-8") as f:
                f.write(f"{count}\t{url}\n")
        for url, count in folders:
            with open("write1.txt", mode="a", encoding="utf-8") as f:
                f.write(f"{count}\t{url}\n")
