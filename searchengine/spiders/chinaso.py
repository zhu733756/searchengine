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


class ChinaSoSpider(scrapy.Spider):
    name = 'chinaso'
    allowed_domains = ['www.chinaso.com']
    # start_urls = ['https://www.chinaso.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        # keywords = '酒店'
        pagenum = int(pagenum)
        super().__init__(*args, **kwargs)
        self.start_urls = [
            'http://www.chinaso.com/search/pagesearch.htm?q={}&page={}'.format(keywords, pagenum)]

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
            match = re.match('(\d+)年(\d+)月(\d+)日',
                             time) or re.match('(\d+)-(\d+)-(\d+)', time)
            if match:
                year = match.group(1)
                month = match.group(2)
                day = match.group(3)
                return '{}年{}月{}日'.format(year, month, day)
        return ''

    def parse(self, response):
        # with open('c:/work/baidu.html', 'w', encoding='utf-8') as file:
        #     file.write(response.text)
        items = response.css('.mainWrapper .seResult .reItem')
        for item in items:
            title = ''.join(item.css('h2 a ::text').extract()).strip()
            if not title:
                title = ''.join(item.css('header h3 ::text').extract()).strip()
            # print(title)
            if not title:
                print('!!!no title')
                continue
            # url
            url = item.css('h2 a:not([href=""])::attr(href)').extract_first('')
            if not url:
                url = item.css('header a::attr(href)').extract_first('')
            # print(url)
            if url:
                url = response.urljoin(url)
            else:
                # print('!!!no url')
                continue
            # img
            burl = item.css('.imgVM ::attr(burl)').extract_first(
                '').split("|")[0]
            purl = item.css('.imgVM ::attr(purl)').extract_first('')
            # print('img:', img)
            if burl:
                img = f"http://n5.map.pg0.cn/{burl}.jpg"
            else:
                img = purl
            img = response.urljoin(img)
            # time
            time = item.xpath(
                './/p[@class="snapshot"]/span/text()').re("\d{4}-\d{1,2}-\d{1,2}")
            time = self.parsetime("".join(time))
            # print('time:', time)
            # content
            target_content = item.xpath(".//div[contains(@class,'reNewsContL')]/p[1]/text() | .//div[contains(@class,'reNewsContL')]/p[1]/em/text() ") or \
                item.xpath(
                    ".//div[contains(@class, 'reNewsWrapper')]/div/p/text() | .//div[contains(@class, 'reNewsWrapper')]/div/p/em/text() ")

            content = "".join(i.extract() for i in target_content)
            content = "".join(re.split("\s+", content))
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl=img, time=time)


if __name__ == "__main__":

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    process = CrawlerProcess(get_project_settings())
    process.crawl(ChinaSoSpider, keywords='张大奕', pagenum='1')
    process.start()
