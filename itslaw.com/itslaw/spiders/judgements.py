# -*- coding: utf-8 -*-
import scrapy


class JudgementsSpider(scrapy.Spider):
    name = 'judgements'
    allowed_domains = ['itslaw.com']
    start_urls = ['http://itslaw.com/']

    def parse(self, response):
        pass
