# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
# from scrapy.utils.response import open_in_browser
from searchengine.items import SearchengineItem
from datetime import datetime, date, timedelta
import re

class BingSpider(scrapy.Spider):
    name = 'bing'
    allowed_domains = ['bing.com']
    # start_urls = ['http://cn.bing.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pagenum = int(pagenum)
        self.start_urls = ['https://cn.bing.com/search?q={}&first={}'.format(keywords, (pagenum-1)*10+1)]

    def parse(self, response):
        items = response.css('#b_results .b_algo')
        # if not items:
        #     with open('c:/work/crawl.htm', 'w', encoding="utf-8") as html_file:
        #         html_file.write(response.text)
        #     print(response.request.headers)
        for item in items:
            title = ''.join(item.css('.b_title h2 a *::text').extract())
            url = item.css('.b_title h2 a::attr(href)').extract_first('')
            if url:
                url = response.urljoin(url)
            content = ''.join(item.css('.b_caption p ::text').extract())
            content = ''.join(content.split()).strip()
            time = ''
            match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', content)
            if match:
                time = match.group()
            else:
                match = re.match(r'(\d+)( 天前|daysago)', content)
                if match:
                    days = match.group(1)
                    itemdate = date.today() - timedelta(days=int(days))
                    time = '{}-{}-{}'.format(itemdate.year, itemdate.month, itemdate.day)
                else:
                    match = re.match(r'(\d+)( 小时前|hoursago)', content)
                    if match:
                        hours = match.group(1)
                        itemtime = datetime.now() - timedelta(hours=int(hours))
                        time = itemtime.strftime('%Y-%m-%d %H:%M')
                        
            # print(title, url)
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl='', time=time)
