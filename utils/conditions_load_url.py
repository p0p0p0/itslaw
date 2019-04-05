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
            r.sadd("conditions:count1", url)

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

if __name__ == "__main__":
    count(Path("../docs/url.merged.txt"))