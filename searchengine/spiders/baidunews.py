# -*- coding: utf-8 -*-
import scrapy
from searchengine.items import SearchengineItem
import re
from datetime import datetime, timedelta


class BaidunewsSpider(scrapy.Spider):
    name = 'baidunews'
    # allowed_domains = ['news.baidu.com']
    # start_urls = ['http://news.baidu.com/']

    def __init__(self, keywords=None, pagenum=1, sorttype=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pagenum = int(pagenum)
        self.start_urls = ['https://www.baidu.com/s?rtt={}&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={}&pn={}'.format(
            sorttype, keywords, (pagenum - 1) * 10)]

    def parse(self, response):
        items = response.css('#content_left .result')
        # if not items:
        #     with open('c:/work/crawl.htm', 'w', encoding="utf-8") as html_file:
        #         html_file.write(response.text)
        #     print(response.request.headers)
        for item in items:
            title = ''.join(item.css('h3 a *::text').extract()).strip()
            url = item.css('h3 a::attr(href)').extract_first('')
            if url:
                url = response.urljoin(url)
            pic = item.css('img.c-img::attr(src)').extract_first('')
            if pic:
                pic = response.urljoin(pic)

            content = ''.join(item.xpath(
                './div[contains(@class,"c-summary")]/node()[not(self::p) and not(self::span)]/text() | ./div[contains(@class,"c-summary")]/text()').extract())
            content = ''.join(content.split())

            write = ''.join(
                item.css('.c-summary .c-author *::text').extract()).strip()
            (author, time, *_) = write.split()
            match = re.match('(\d+)小时前', time)
            if match:
                hours = match.group(1)
                arttime = datetime.now() - timedelta(hours=int(hours))
                time = arttime.strftime(
                    '%Y{}%m{}%d{} %H:%M').format('年', '月', '日')
            # print('===', title.strip(), url)
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author=author, picUrl=pic, time=time)
