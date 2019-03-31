# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from redis import Redis, ConnectionPool
from scrapy.conf import settings


class ItslawPipeline(object):
    def __init__(self):
        self.pool = ConnectionPool(host=settings["REDIS_HOST"], port=settings["REDIS_PORT"], decode_responses=True, db=0)
        self.r = Redis(connection_pool=self.pool)

    def process_item(self, item, spider):
        doc = item["id"]
        if not self.r.sismember("itslaw:start", doc) or not self.r.sismember("itslaw:crawled", doc):
            res = self.r.sadd("itslaw:id", doc)
            if 1 == res:
                spider.log(f"[+] {doc}")
        return item
