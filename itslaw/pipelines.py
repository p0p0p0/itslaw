# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from redis import Redis, ConnectionPool
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class ItslawPipeline(object):
    def process_item(self, item, spider):
        doc = item["id"]
        if not spider.r.sismember("itslaw:jid", doc) and not spider.r.sismember("itslaw:crawled", doc):
            res = spider.r.sadd("itslaw:id", doc)
            if 1 == res:
                spider.logger.debug(f"[+] {doc}")
        else:
            DropItem("item crawled")
        return item


class CasePipeline(object):
    def process_item(self, item, spider):
        fullJudgement = item["item"]
        jid = fullJudgement["id"]
        spider.r.sadd("itslaw:jid", jid)
        spider.r.sadd("itslaw:judgement", json.dumps(fullJudgement, ensure_ascii=False))
        spider.logger.debug(f"[+] {jid} saved.")
        return item