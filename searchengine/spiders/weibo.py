# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from searchengine.items import SearchengineItem
from datetime import datetime


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['www.weibo.com']
    start_urls = ['http://www.weibo.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pagenum = int(pagenum)
        self.start_urls = ['https://s.weibo.com/article?q={}&Refer=weibo_article&page={}'.format(keywords, pagenum)]

    def parse(self, response):
        items = response.css('#pl_feedlist_index .card-wrap .card-article-a')
        # if not items:
        #     with open('c:/work/crawl.htm', 'w', encoding="utf-8") as html_file:
        #         html_file.write(response.text)
        #     print(response.request.headers)
        for item in items:
            title = ''.join(item.css('h3 a ::text').extract())
            url = item.css('h3 a::attr(href)').extract_first('')
            url = response.urljoin(url)
            content = ''.join(item.css('.content .detail .txt ::text').extract())
            pic = item.css('.content .pic img::attr(src)').extract_first('')
            if pic:
                pic = response.urljoin(pic)
            author = item.css('.content .detail .act>div span:first-child ::text').extract_first('')
            time = item.css('.content .detail .act>div span:last-child ::text').extract_first('')
            curtime = datetime.now()
            if '今天' in time:
                curtime = datetime.now()
                time = time.replace('今天', '{}月{}日 '.format(curtime.month, curtime.day))
            if '年' not in time:
                time = '{}年{}'.format(curtime.year, time)
            # print(title, url)
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author=author, picUrl=pic, time=time)
