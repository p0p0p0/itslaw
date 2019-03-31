import pymongo

client = pymongo.MongoClient(host="129.211.118.148")

db = client.atersoft
coll = db.wusong_judgements

docs = coll.find({})
# too slow
for doc in docs:
    print(doc["_id"])
    break
