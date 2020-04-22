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


class Ss360Spider(scrapy.Spider):
    name = 'ss_360'
    allowed_domains = ['www.so.com']
    # start_urls = ['https://www.so.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        # keywords = '酒店'
        pagenum = int(pagenum)
        super().__init__(*args, **kwargs)
        self.start_urls = [
            'https://www.so.com/s?q={}&pn={}&src=srp_paging&fr=tab_news'.format(keywords, pagenum)]

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
        items = response.css('#container #main .result .res-list')
        for item in items:
            title = ''.join(item.css('h3 a ::text').extract()).strip()
            if not title:
                title = ''.join(item.css('header h3 ::text').extract()).strip()
            # print(title)
            if not title:
                print('!!!no title')
                continue
            # url
            url = item.css('h3 a:not([href=""])::attr(href)').extract_first('')
            if not url:
                url = item.css('header a::attr(href)').extract_first('')
            # print(url)
            if url:
                url = response.urljoin(url)
            else:
                # print('!!!no url')
                continue
            # img
            img = item.css('.res-comm-img ::attr(data-isrc)').extract_first(
                '') or item.xpath(".//div[@class='mh-first-img']//img/@src").extract() or ''
            # print('img:', img)
            if img:
                img = img if isinstance(img, str) else img[0]
                img = response.urljoin(img)
            # time
            time = item.css('span.gray::text').extract_first(
                '') or item.css('span.mh-time::text').extract_first('')
            time = self.parsetime(time)
            # print('time:', time)
            # content
            target_content = item.xpath(".//div[contains(@class,'res-comm-con')]/p[@class='res-desc']/text() | .//div[contains(@class,'res-comm-con')]/p[@class='res-desc']/em/text()") or \
                item.xpath(".//div[contains(@class, 'res-rich')]/div/text() | .//div[contains(@class, 'res-rich')]/div/em/text()") or \
                item.xpath(".//div[contains(@class, 'res-rich')]/text() | .//div[contains(@class, 'res-rich')]/em/text()") or \
                item.xpath(".//p[@class='mh-first-cont']/text()")

            content = "".join(i.extract() for i in target_content)
            content = "".join(re.split("\s+", content))
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl=img, time=time)


if __name__ == "__main__":

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    process = CrawlerProcess(get_project_settings())
    process.crawl(Ss360Spider, keywords='张大奕', pagenum='1')
    process.start()
