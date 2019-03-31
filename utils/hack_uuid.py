from uuid import uuid5, NAMESPACE_OID, uuid1, uuid3
from urllib.parse import urlencode, urlparse

# print(uuid3(NAMESPACE_OID, "itslaw黄斌"))

url = "https://www.itslaw.com/api/v1/judgements/judgement/f655fe48-04e1-488f-ba4e-9c2b35cca6e9/relatedJudgements?pageNo=6&pageSize=5"

base = url.split("?")[0]

print(base)
print(urlencode(base, {"a":1}))