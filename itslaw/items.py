# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JudgementItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()

class CaseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item = scrapy.Field()