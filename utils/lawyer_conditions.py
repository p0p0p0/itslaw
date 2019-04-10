import json
from urllib.parse import urlencode
from time import sleep
import logging

from requests import Session

["licenseYear", "profileType", "geo", "lawFirm", "reason"]
logger = logging.getLogger(__name__)
logger.addFilter(logging.Filter(name=__name__))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(filename)s] %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

url = "https://www.itslaw.com/api/v1/subSites?subSiteCode=bj"
base_url = "https://www.itslaw.com/api/v1/pfofiles?"

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
    "Cookie": "_t=0e9084b2-59b6-4cab-985f-be99b553e944; LXB_REFER=mail.qq.com; Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008=1554555977,1554601580,1554601590,1554601609; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1554555977,1554601580,1554601591,1554601609; showSubSiteTip=false; subSiteCode=bj; sessionId=6f3b2542-3c7f-4ca5-a62c-5c17b3f42f51; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008=1554891908; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1554891908", 
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
            
            profileSearchResult = data["profileSearchResult"]
            totalCount = profileSearchResult["totalCount"]
            if 0 == totalCount:
                return read, write
            # 带top开头的都不是过滤条件
            # 地域
            geoResults = profileSearchResult["geoResults"]            
            # 律所
            lawFirmResults = profileSearchResult["lawFirmResults"]
            # 执业年限
            licenseYearResults = profileSearchResult["licenseYearResults"]            
            # 名片类型
            profileTypeResults = profileSearchResult["profileTypeResults"]            
            # 案由
            reasonResults = profileSearchResult["reasonResults"]
            # 搜索结果
            profiles = profileSearchResult["profiles"]
            
            logger.debug(totalCount)

            if "geo" == filter:
                code = 2
                for each in geoResults:
                    condition_parser(filter, code, each, read, write)

            elif "lawFirm" == filter:
                code = 3
                for each in lawFirmResults:
                    condition_parser(filter, code, each, read, write)

            elif "reason" == filter:
                code = 6
                for each in reasonResults:
                    condition_parser(filter, code, each, read, write)


            # "下面的不需要解析, 直接组合"
            elif "licenseYear" == filter:
                code = 7
                for each in licenseYearResults:
                    level = each["id"]
                    name = each["name"]
                    count = each["count"]
                    if 400 >= count:
                        read.append((f"{filter}+{level}+{code}+{name}", count))
                    else:
                        write.append((f"{filter}+{level}+{code}+{name}", count))

            elif "profileType" == filter:
                code = 5
                for each in profileTypeResults:
                    level = each["id"]
                    name = each["name"]
                    count = each["count"]
                    if 400 >= count:
                        read.append((f"{filter}+{level}+{code}+{name}", count))
                    else:
                        write.append((f"{filter}+{level}+{code}+{name}", count))

            for each in profiles:
                # logger.debug(each["id"])
                with open("profiles.txt", mode="a", encoding="utf-8") as f:
                    f.write(each["id"] + "\n")

            # for condition in read:
            #     logger.debug(condition)
            # for condition in write:
            #     logger.debug(condition)

            # with open(f"{filter}.txt", mode="w", encoding="utf-8") as f:
            #     f.write("\n".join(conditions))
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
    count = int(count) if count else 0
    children = each.get("children", None)
    if children:
        for child in children:
            condition_parser(filter, code, child, read, write)
    else:
        if 400 >= count:
            read.append((f"{filter}+{level}+{code}+{name}", count))
        else:
            write.append((f"{filter}+{level}+{code}+{name}", count))

def get_count(url):
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
            
            profileSearchResult = data["profileSearchResult"]
            totalCount = profileSearchResult["totalCount"]
            return totalCount
            
if __name__ == "__main__":
    s = Session()
    # 生成初始链接
    
    # url = f"https://www.itslaw.com/api/v1/profiles?startIndex=0&countPerPage=20&sortType=1&conditions=profileType%2B1%2B5%2B%E4%BC%98%E9%80%89%E5%BE%8B%E5%B8%88"
    # files, folders = get_tree(url=url)
    # for url, count in files:
    #     with open("read.txt", mode="a", encoding="utf-8") as f:
    #         f.write(f"{count}\t{url}\n")
    # for url, count in folders:
    #     with open("write.txt", mode="a", encoding="utf-8") as f:
    #         f.write(f"{count}\t{url}\n")
    
    db = {}
    # lines = []

    with open("write.txt", mode="r", encoding="utf-8") as w:
        for line in w:
            count, url = line.strip().split()
            db[url] = count
            # lines.append((count, url))
    
    for url in db:
        print(url, db[url])
        if "0" != db[url]:
            continue
        count = get_count(url)
        db[url] = count
        print(url, count)
        with open("read.txt", mode="a", encoding="utf-8") as f:
            f.write(f"{count}\t{url}\n")

    
    # for count, url in lines:
    #     files, folders = get_tree(url=url)
    #     logger.debug(len(files))
    #     logger.debug(len(folders))
    #     # for each in files:
    #     #     logger.debug(f"files: {each}")
    #     # for each in folders:
    #     #     logger.debug(f"folders: {folders}")

    #     for url, count in files:
    #         with open("read.txt", mode="a", encoding="utf-8") as f:
    #             f.write(f"{count}\t{url}\n")
    #     for url, count in folders:
    #         with open("write1.txt", mode="a", encoding="utf-8") as f:
    #             f.write(f"{count}\t{url}\n")
