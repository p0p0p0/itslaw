from redis import Redis

r = Redis()
# res = r.sdiffstore("itslaw:start", "itslaw:start", "itslaw:crawled")
res = r.sdiffstore("itslaw:id", "itslaw:id", "itslaw:jid")
print(res)