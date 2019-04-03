from redis import Redis
from random import choices
r = Redis()
# res = r.sdiffstore("itslaw:start", "itslaw:start", "itslaw:crawled")
# res = r.sdiffstore("itslaw:id", "itslaw:id", "itslaw:jid")
# res = r.sdiff("itslaw:id", "itslaw:jid")
a = set(i for i in range(10))
print(choices(a,k=2))