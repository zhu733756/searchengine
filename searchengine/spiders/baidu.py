# -*- coding: utf-8 -*-
import scrapy
from searchengine.items import SearchengineItem
import re
from datetime import datetime, timedelta, date
from collections import OrderedDict

class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['www.baidu.com']
    # start_urls = ['http://www.baidu.com/']

    def __init__(self, keywords=None, pagenum=1, *args, **kwargs):
        # keywords = '酒店'
        pagenum = int(pagenum)
        super().__init__(*args, **kwargs)
        self.start_urls = ['https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd={}&pn={}'.format(keywords, (pagenum-1)*10)]

    def parsetime(self, time:str):
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
        items = response.css('#content_left .result.c-container,.result-op.c-container')
        for item in items:
            classname = item.css('::attr(class)').extract_first('')
            # print('======', classname)
            #title
            title = ''.join(item.css('h3 a ::text').extract()).strip()
            if not title:
                title = ''.join(item.css('header h3 ::text').extract()).strip()
            # print(title)
            if not title:
                # print('!!!no title')
                continue
            #url
            url = item.css('h3 a:not([href=""])::attr(href)').extract_first('')
            if not url:
                url = item.css('header a::attr(href)').extract_first('')
            # print(url)
            if url:
                url = response.urljoin(url)
            else:
                # print('!!!no url')
                continue
            #img
            img = item.css('img.c-img::attr(src)').extract_first('')
            # print('img:', img)
            if img:
                img = response.urljoin(img)
            #time
            time = item.css('.c-abstract .newTimeFactor_before_abs::text').extract_first('')
            time = self.parsetime(time)
            # print('time:', time)
            #content
            content = ''
            if 'result-op' in classname:
                content += ''.join(i.strip() for i in item.css('.c-row *::text').extract()).strip()
                content += ''.join(i.strip() for i in item.css('td *::text').extract()).strip()
            else: #class==".result"
                content = ''.join(i.strip() for i in item.css('.c-abstract *::text').extract()).strip()
            # print(content)
            yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl=img, time=time)

            # #children 先不要二层了，二层样式太混乱
            # children = item.css('.c-row .c-span6:not(.general_image_pic)')
            # if len(children) == 0:
            #     children = item.css('.c-row')
            # for child in children:
            #     ctitle = ''.join(i.strip() for i in child.css('a::text').extract()).strip()
            #     curl = child.css('a::attr(href)').extract_first('')
            #     cimg = child.css('img::attr(src)').extract_first('')
            #     ccontent = ''.join(i.strip() for i in child.css('::text').extract()).strip()
            #     print('-----------')
            #     print('>>>>title:', ctitle)
            #     print('>>>>curl:', curl)
            #     print('>>>>cimg:', cimg)
            #     print('>>>>content:', ccontent)

            # title = ''
            # url = ''
            # title-elem = item.css('h3 a') #企业信息 这类条目会有两个h3，第一个是个空的
            # for one in title-elem:
            #     title = ''.join(one.css('*::text').extract_first('')).strip()
            #     if title:
            #         url = one.css('::attr(href)').extract_first('')
            #         if url:
            #             url = response.urljoin(url)
            #             break
            #         else:
            #             continue
            #     else:
            #         continue

            # if not title or not url:
            #     continue

            # title = ''.join(item.css('h3 a ::text').extract()).strip()
            # if not title:
            #     continue
            # url = item.css('h3 a::attr(href)').extract_first('')
            # if url:
            #     url = response.urljoin(url)
            # content = ''.join(item.css('*:not(style):not(script)::text').extract())
            # pic = item.css('img::attr(src)').extract_first('')
            # if pic:
            #     pic = response.urljoin(pic)

            # time = item.css('.c-abstract .newTimeFactor_before_abs::text').extract_first('')
            # time = time.strip('- ')
            # if '前' in time:
            #     if '天' in time:
            #         match = re.match('(\d+)天', time)
            #         if match:
            #             days = match.group(1)
            #             timeval = date.today() - timedelta(days=int(days))
            #             time = '{}年{}月{}日'.format(timeval.year, timeval.month, timeval.day)
            #     elif '小时' in time:
            #         match = re.match('(\d+)小时', time)
            #         if match:
            #             hours = match.group(1)
            #             timeval = datetime.now() - timedelta(hours=int(hours))
            #             time = timeval.strftime('%Y{}%m{}%d %H:%M').format('年', '月', '日')
            #     elif '分钟' in time:
            #         match = re.match('(\d+)分', time)
            #         if match:
            #             mins = match.group(1)
            #             timeval = datetime.now() - timedelta(mins=int(mins))
            #             time = timeval.strftime('%Y{}%m{}%d %H:%M').format('年', '月', '日')
            # # print('===', title, url)
            # # print(content)
            # yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl=pic, time=time)

            # # 是否有子项目
            # classname = item.css('::attr("class")').extract_first('')
            # if 'result-op' in classname:
            #     links = OrderedDict()
            #     for onelink in item.css('a'):
            #         url2 = onelink.css('::attr(href)').extract_first('')
            #         if url2:
            #             url2 = response.urljoin(url2)
            #         if url2 == url:
            #             continue
            #         linkobj = None
            #         if url2 in links:
            #             linkobj = links[url2]
            #         else:
            #             links[url2] = {}
            #             linkobj = links[url2]

            #         title2 = ' '.join(txt.strip() for txt in onelink.css('*::text').extract()).strip()
            #         if title2:
            #             if 'title' not in linkobj:
            #                 linkobj['title'] = title2
            #         pic = onelink.css('img::attr(src)').extract_first('')
            #         if pic:
            #             pic = response.urljoin(pic)
            #             if 'pic' not in linkobj:
            #                 linkobj['pic'] = pic
            #     for url in links:
            #         onelink = links[url]
            #         yield SearchengineItem(title=onelink['title'] if 'title' in onelink else '', href=url, summary='', author='', picUrl=onelink['pic'] if 'pic' in onelink else '', time=time)
            # else:
            #     subitems = item.css('table tr').extract()
            #     if not subitems:
            #         continue
                
            #     for subitem in subitems:
            #         title2 = ' '.join(txt.strip() for txt in subitem.css('::text').extract()).strip()
            #         url2 = subitem.css('a::attr(href)').extract_first('')
            #         print(title2, url2)
            #         yield SearchengineItem(title=title2, href=url2, summary='', author='', picUrl='', time=time)

        # items = response.css('#content_left .result')
        # # if not items:
        # #     with open('c:/work/crawl.htm', 'w', encoding="utf-8") as html_file:
        # #         html_file.write(response.text)
        # #     print(response.request.headers)
        # for item in items:
        #     title = ''.join(item.css('h3 a ::text').extract()).strip()
        #     url = item.css('h3 a::attr(href)').extract_first('')
        #     if url:
        #         url = response.urljoin(url)
        #     content = ''.join(item.css('.c-abstract *::text').extract())
        #     pic = item.css('img::attr(src)').extract_first('')
        #     if pic:
        #         pic = response.urljoin(pic)

        #     time = item.css('.c-abstract .newTimeFactor_before_abs::text').extract_first('')
        #     time = time.strip('- ')
        #     if '前' in time:
        #         if '天' in time:
        #             match = re.match('(\d+)天', time)
        #             if match:
        #                 days = match.group(1)
        #                 timeval = date.today() - timedelta(days=int(days))
        #                 time = '{}年{}月{}日'.format(timeval.year, timeval.month, timeval.day)
        #         elif '小时' in time:
        #             match = re.match('(\d+)小时', time)
        #             if match:
        #                 hours = match.group(1)
        #                 timeval = datetime.now() - timedelta(hours=int(hours))
        #                 time = timeval.strftime('%Y{}%m{}%d %H:%M').format('年', '月', '日')
        #         elif '分钟' in time:
        #             match = re.match('(\d+)分', time)
        #             if match:
        #                 mins = match.group(1)
        #                 timeval = datetime.now() - timedelta(mins=int(mins))
        #                 time = timeval.strftime('%Y{}%m{}%d %H:%M').format('年', '月', '日')
        #     # print('===', title, url)
        #     # print(content)
        #     yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl=pic, time=time)

        # items = response.css('#content_left .result-op.c-container')
        # for item in items:
        #     title = ''.join(item.css('h3 a ::text').extract()).strip()
        #     url = item.css('h3 a::attr(href)').extract_first('')
        #     if url:
        #         url = response.urljoin(url)
        #     pic = item.css('img.c-img::attr(src)').extract_first('')
        #     if pic:
        #         pic = response.urljoin(pic)
        #     content = ''.join(item.css('*:not(style):not(script)::text').extract())
        #     content = ''.join(content.split())

        #     # print('===', title, url)
        #     # print(content)
        #     yield SearchengineItem(title=title, href=url, summary=content, author='', picUrl=pic, time='')

        #     child_links = {}
        #     img_links = {}
        #     child_items = item.css('a')
        #     for one_item in child_items:
        #         link = one_item.css('::attr(href)').extract_first()
        #         if link:
        #             link = response.urljoin(link)
        #         else:
        #             continue
                
        #         ttl = ''.join(''.join(one_item.css('::text').extract()).split())
        #         pic = one_item.css('img.c-img::attr(src)').extract_first('')
        #         if pic:
        #             pic = response.urljoin(pic)
        #             img_links[link] = pic
        #         if link in child_links:
        #             child_links[link] += ttl
        #         else:
        #             child_links[link] = ttl

        #     for link in child_links:
        #         # print('>>>', link, child_links[link], img_links[link] if link in img_links else 'no-pic')
        #         picurl = img_links[link] if link in img_links else ''
        #         yield SearchengineItem(title=child_links[link], href=link, summary='', author='', picUrl=picurl, time='')
