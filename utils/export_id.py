import json
import pymongo
import redis

def export(collection):
    client = pymongo.MongoClient(port=27017)
    db = client.atersoft
    coll = db[collection]
    for i, doc in enumerate(coll.find({}), start=24541093):
        filename = f"{(i//100000)+1:#03}"
        jid = doc["_id"]
        if not isinstance(jid, (str,)):
            with open(f"error.jl", mode="a", encoding="utf-8") as f:
                f.write(json.dumps(str(jid), ensure_ascii=False) + "\n")
            jid = "ObjectId"
            doc = {"error": "id type error"}

        with open("ids_crawled2.dat", mode="a", encoding="utf-8") as t:
            t.write(jid + "\n")
        with open(f"{filename}.jl", mode="a", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def dump(count):
    r = redis.Redis()
    ret = set()
    for i in range(count):
        item = r.spop("itslaw:id")
        jid = str(item, encoding="utf-8")
        ret.add(jid)
    with open("ids.txt", mode="w", encoding="utf-8") as f:
        f.write("\n".join(ret))


def dump_to_txt():
    r = redis.Redis()
    ids = r.smembers("itslaw:id")
    for each in ids:
        jid = str(each, encoding="utf-8")
        with open("ids_to_crawl.dat", mode="a", encoding="utf-8") as f:
            f.write(jid + "\n")


def load():
    r = redis.Redis()
    with open("jufaanli_case_number.dat", mode="r", encoding="utf-8") as f:
        for line in f:
            jid = line.strip()
            r.sadd("jufaanli:casenumber", jid)


if __name__ == "__main__":
    # export("wusong_judgements_001")
    load()
