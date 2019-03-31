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




if __name__ == "__main__":
    export("law_anhui")