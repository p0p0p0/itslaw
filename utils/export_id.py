import pymongo
import redis

def export(collection):
    r = redis.Redis()
    client = pymongo.MongoClient()
    db = client.atersoft
    coll = db[collection]
    for doc in coll.find({}):
        jid = doc["judgementId"]
        if not r.sismember("itslaw:start", jid) and not r.sismember("itslaw:crawled", jid):
            r.sadd("itslaw:id", jid)
            print(f"[+] {jid}")

def dump(count):
    r = redis.Redis()
    ret = set()
    for i in range(count):
        item = r.spop("itslaw:id")
        jid = str(item, encoding="utf-8")
        ret.add(jid)
    with open("ids.txt", mode="w", encoding="utf-8") as f:
        f.write("\n".join(ret))

def load():
    r = redis.Redis()
    with open("ids.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            jid = line.strip()
            r.sadd("itslaw:id", jid)


if __name__ == "__main__":
    dump(500000)
