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

if __name__ == "__main__":
    load()