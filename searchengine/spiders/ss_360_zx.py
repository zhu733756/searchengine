# -*- coding: utf-8 -*-
import scrapy
from pathlib import Path
import sys
project_path = str(Path(__file__).parent.parent.parent)
if project_path not in sys.path:
    sys.path.append(project_path)
from searchengine.items import SearchengineItem
import re
from datetime import datetime, timedelta, date
from collections import OrderedDict
from scrapy.selector import Selector


class Ss360ZZSpider(scrapy.Spider):
    name = 'ss_360_zx'
    allowed_domains = ['www.so.com']
    # start_urls = ['https://www.so.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        # keywords = '酒店'
        pagenum = int(pagenum)
        super().__init__(*args, **kwargs)
        self.start_urls = [
            'https://news.so.com/ns?q={}&pn={}&tn=news&rank=rank&j=0&nso=15&tp=26&nc=0&src=page'.format(keywords, pagenum)]

    def parsetime(self, time: str):
        if '前' in time:
            if '天' in time:
                match = re.match('(\d+)天', time)
                if match:
                    days = match.group(1)
                    timeval = date.today() - timedelta(days=int(days))
                    return '{}年{}月{}日'.format(timeval.year, timeval.month, timeval.day)
            elif '小时' in time:
                match = re.match('(\d+)小时', time)
                if match:
                    hours = match.group(1)
                    timeval = datetime.now() - timedelta(hours=int(hours))
                    return timeval.strftime('%Y{}%m{}%d %H:00').format('年', '月', '日')
            elif '分钟' in time:
                match = re.match('(\d+)分', time)
                if match:
                    mins = match.group(1)
                    timeval = datetime.now() - timedelta(minutes=int(mins))
                    return timeval.strftime('%Y{}%m{}%d %H:%M').format('年', '月', '日')
        elif time == "刚刚":
            timeval = datetime.now()
            return timeval.strftime('%Y{}%m{}%d %H:00').format('年', '月', '日')
        else:
            match = re.match('(\d+)年(\d+)月(\d+)日', time)
            if match:
                year = match.group(1)
                month = match.group(2)
                day = match.group(3)
                return '{}年{}月{}日'.format(year, month, day)
        return ''

    def parse(self, response):
        # with open('c:/work/baidu.html', 'w', encoding='utf-8') as file:
        #     file.write(response.text)
        items = response.css('#container #main .result_wrap .res-list')
        for item in items:
            title = ''.join(item.css('a ::attr(title)').extract()).strip()
            if not title:
                continue
            # url
            url = item.css('a:not([href=""])::attr(href)').extract_first('')
            if not url:
                url = item.css('header a::attr(href)').extract_first('')
            # print(url)
            if url:
                url = response.urljoin(url)
            else:
                # print('!!!no url')
                continue
            # img
            img = item.xpath(
                './/a[@class="group-img-link"]//img/@src').extract() or ''
            if img:
                img = img if isinstance(img, str) else img[0]
                img = response.urljoin(img)
            # time
            time = item.xpath(
                "//span[@class='sitename']/../span[last()]/text()").extract_first('')
            time = self.parsetime(time)
            # print('time:', time)
            # content
            author = item.css('span.stname::text').extract_first('')
            content = item.xpath(
                './/div[@class="summary"]/text() | .//div[@class="summary"]/em/text()').extract()
            content = "".join(content)
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author=author, picUrl=img, time=time)


if __name__ == "__main__":

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    process = CrawlerProcess(get_project_settings())
    process.crawl(Ss360ZZSpider, keywords='刘德华', pagenum='1')
    process.start()
