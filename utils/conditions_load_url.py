from pathlib import Path
from urllib.parse import urlunparse, unquote
from datetime import datetime
from collections import Counter
from pprint import pprint

import pymongo
from redis import Redis


client = pymongo.MongoClient()
db = client.conditions
coll = db.page_other

r = Redis()

def load_to_mongodb(path):
    if not path:
        raise ValueError("Path needed")
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            update_time = datetime.now().date().isoformat()
            count, url = line.strip().split()
            doc = {
                "count": count,
                "url":url,
                "update_time": update_time,
                "ids": []
            }
            res = coll.insert_one(doc)
            if not res.acknowledged:
                print(line.strip())

def load_to_redis(path):
    if not path:
        raise ValueError("Path needed")
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            count, url = line.strip().split()
            for i in range(0, int(count), 20):
                if i > 400:
                    break
                p = url.replace("startIndex=0", f"startIndex={i}")
                r.sadd(f"condition:all", p)
                if int(count) > 400:
                    p = p.replace("sortType=1", "sortType=2")
                    r.sadd(f"condition:all", p)


def count(path):
    if not path:
        raise ValueError("Path needed")
    ret = 0
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            count, url = line.strip().split()
            count = int(count)
            if count % 20 == 0:
                ret += count // 20 + 1
            else:
                ret += count //20 +2
        print(ret)


def filter_pages():
    members = r.smembers("condition:all")
    for each in members:
        if str(each, encoding="utf-8").startswith("https://www.itslaw.com/api/v1/caseFiles?startIndex=0"):
            r.sadd("condition:one", each)
        else:
            r.sadd("condition:more", each)

def split_pages(part):
    members = r.smembers("condition:more")
    for i, each in enumerate(members):
        p = i % part
        r.sadd(f"condition:more{p}", each)
         

def import_search_word():
    for i in range(1, 20000):
        url = f"https://www.itslaw.com/api/v1/caseFiles?startIndex=0&countPerPage=20&sortType=1&conditions=searchWord%2B%EF%BC%882018%EF%BC%89%E5%86%8002%E6%89%A7{i}%E5%8F%B7%2B1%2B%EF%BC%882018%EF%BC%89%E5%86%8002%E6%89%A7{i}%E5%8F%B7"
        r.sadd("condition:searchword", url)

if __name__ == "__main__":
    # load_to_redis(Path("condition.txt"))
    # filter_pages()
    import_search_word()

