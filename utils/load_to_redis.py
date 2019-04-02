import redis

def load():
    r = redis.Redis()
    count = 0
    with open("1.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            jid = line.strip()
            if jid:
                if not r.sismember("itslaw:start", jid) and not r.sismember("itslaw:crawled", jid):
                    res = r.sadd("itslaw:id", jid)
                    if res:
                        print(f"[+]\t{count}\t{jid}")
                        count += 1

def pull(count):
    r1 = redis.Redis()
    r2 = redis.Redis(host="192.168.1.3")
    for i in range(count):
        item = r2.spop("itslaw:id")
        try:
            r1.sadd("itslaw:id", item)
        except Exception as e:
            r2.sadd("itslaw:id", item)
            print(e)

if __name__ == "__main__":
    pull(10000)