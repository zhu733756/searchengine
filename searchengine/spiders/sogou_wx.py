# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from searchengine.items import SearchengineItem
from datetime import datetime


class SogouWxSpider(scrapy.Spider):
    name = 'sogou_wx'
    allowed_domains = ['weixin.sogou.com']
    # start_urls = ['https://weixin.sogou.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pagenum = int(pagenum)
        self.start_urls = ['https://weixin.sogou.com/weixin?type=2&query={}&page={}'.format(keywords, pagenum)]

    def parse(self, response):
        items = response.css('.news-list li')
        for item in items:
            title = ''.join(item.css('.txt-box h3 a ::text').extract())
            url = item.css('.txt-box h3 a::attr(data-share)').extract_first()
            url = response.urljoin(url)
            content = ''.join(item.css('.txt-box p ::text').extract())
            pic = item.css('.img-box img::attr(src)').extract_first('')
            if pic:
                pic = response.urljoin(pic)

            author = item.css('.txt-box .s-p>a::text').extract_first('')
            time = item.css('.txt-box .s-p>.s2>script::text').extract_first('')
            if time:
                timestamp = time.split("'")[1]
                timeval = datetime.fromtimestamp(timestamp)
                time = datetime.strftime(timeval, '%Y年%m月%d %H:%M')
            # print(title, url)
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author=author, picUrl=pic, time=time)
