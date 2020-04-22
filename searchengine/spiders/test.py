# -*- coding: utf-8 -*-
import scrapy


class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['httpbin.org/get']
    start_urls = ['http://httpbin.org/get']

    def parse(self, response):
        print(response.text)
