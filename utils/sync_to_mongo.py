"""
sync to mongodb first, then merge redis judgement id data
"""
import json
from time import sleep
from datetime import datetime

from redis import Redis
import pymongo
from bson import ObjectId


client = pymongo.MongoClient(port=27017)
db = client.atersoft
coll = db.wusong_judgements_006

r = Redis()

def upload():
    while True:
        item = r.spop("itslaw:judgement")
        if not item:
            print("[*] sync done. wait for next 60 secs...")
            sleep(60)
            now = datetime.now().isoformat(timespec="seconds")
            res = r.scard("itslaw:judgement")
            print(f"[{now}] sync {res} items...")
            continue
        try:
            doc = str(item, encoding="utf-8")
            doc = json.loads(doc)
            # r.sadd("itslaw:jid", doc["id"])
            doc["_id"] = doc["id"]
            doc.pop("id")

            coll.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            # res = coll.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            # if res.acknowledged:
            #     print(f"[+] {res.upserted_id}")
        except Exception as e:
            r.sadd("itslaw:judgement", item)
            print(e)
        

def merge_id():
    # for i in range(14):
    #     res = r.sdiffstore(f"itslaw:id{i}", f"itslaw:id{i}", "itslaw:jid")
    #     print(res)
    # for i in range(5):
    #     res = r.sdiffstore(f"itslaw:start{i}", f"itslaw:start{i}", "itslaw:crawled")
    #     print(res)
    res = r.sunionstore("itslaw:crawled", "itslaw:crawled", "itslaw:jid")
    print(res)
    # res = r.sdiffstore("itslaw:id0", "itslaw:id0", "itslaw:jid")
    # print(res)


def dump():
    while True:
        item = r.spop("conditions:crawled")
        if not item:
            break
        try:
            doc = str(item, encoding="utf-8")
            with open("conditions_crawled.txt", mode="a", encoding="utf-8") as f:
                f.write(doc + "\n")
        except Exception as e:
            r.sadd("conditions:crawled", item)
            print(e)
            break


def load():
    with open("docs.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line.strip())
            doc["_id"] = doc["id"]
            doc.pop("id")
            try:
                res = coll.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
                if res.acknowledged:
                    print(f"[+] {res.upserted_id}")
            except Exception as e:
                print(e)

def import_ids():
    with open("ids_to_crawl.dat", mode="r", encoding="utf-8") as f:
        for line in f.readlines():
            r.sadd("itslaw:id0", line.strip())

def split(count):
    # for _ in range(count):
    items = r.spop("itslaw:id1", count)
        # if not item:
        #     break
        # jid = str(item, encoding="utf-8")
    r.sadd("itslaw:id0", *items)


def remove_error():
    with open("error_shodan.jl", mode="r", encoding="utf-8") as f:
        for line in f:
            oid = line.strip()
            res = coll.find_one_and_delete({"_id": ObjectId(oid)})

def modify():
    items = r.smembers("itslaw:failed")
    for item in items:
        url = str(item, encoding="utf-8")
        if url.startswith("http"):
            jid = url.split("=")[-1]
            r.sadd("itslaw:id", jid)
        else:
            r.sadd("itslaw:id", item)

def export():
    for doc in coll.find({})[37851338:]:
        jid = doc.get("_id", "")
        prev_id = doc.get("previousId", "")
        next_id = doc.get("nextId", "")
        court = doc.get("court", "")
        judges = doc.get("judges", "")
        source = doc.get("sourceUrl", "")
        case_number = doc.get("caseNumber", "")
        with open("scraped.dat", mode="a", encoding="utf-8") as f:
            f.write(jid + "\n")
        with open("prev.dat", mode="a", encoding="utf-8") as f:
            f.write(prev_id + "\n")
        with open("next.dat", mode="a", encoding="utf-8") as f:
            f.write(next_id + "\n")
        r.sadd("itslaw:court", json.dumps(court, ensure_ascii=False))
        for judge in judges:
            r.sadd("itslaw:judge", json.dumps(judge, ensure_ascii=False))
        with open("source.dat", mode="a", encoding="utf-8") as f:
            f.write(source + "\n")
        with open("casenumber.dat", mode="a", encoding="utf-8") as f:
            f.write(case_number + "\n")

def split_to_parts(part):
    members = r.smembers("itslaw:id")
    for i, each in enumerate(members):
        p = i % part
        r.sadd(f"itslaw:id{p}", each)

if __name__ == "__main__":
    # upload()
    # split(100000)
    # split_to_parts(6)
    merge_id()
    # import_ids()

