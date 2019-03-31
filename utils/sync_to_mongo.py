"""
sync to mongodb first, then merge redis judgement id data
"""

import json

from redis import Redis
import pymongo


client = pymongo.MongoClient()
db = client.atersoft
coll = db.wusong_judgements_000

r = Redis()

def upload():
    docs = r.smembers("itslaw:judgement")
    print(len(docs))
    for doc in docs:
        doc = str(doc, encoding="utf-8")
        doc = json.loads(doc)
        doc["_id"] = doc["id"]
        doc.pop("id")
        res = coll.insert_one(doc)
        if not res.acknowledged:
            print(f"[-] {res.inserted_id}")

def merge_id():
    res = r.sunionstore("itslaw:crawled", "itslaw:crawled", "itslaw:jid")
    print(res)

if __name__ == "__main__":
    merge_id()