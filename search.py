import sys
import json

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from searchengine.spiders.bing import BingSpider
from searchengine.spiders.sogou_wx import SogouWxSpider
from searchengine.spiders.weibo import WeiboSpider
from searchengine.spiders.baidu import BaiduSpider
from searchengine.spiders.baidunews import BaidunewsSpider
from searchengine.spiders.ss_360 import Ss360Spider
from searchengine.spiders.ss_360_zx import Ss360ZZSpider
from searchengine.spiders.chinaso import ChinaSoSpider
from searchengine.spiders.chinaso_news import ChinaSoNewsSpider

from scrapy.signalmanager import dispatcher


def spider_results(spidername, keywords, pagenum, sorttype):
    spider_class = None
    if spidername == 'bing':
        spider_class = BingSpider
    elif spidername == 'weixin':
        spider_class = SogouWxSpider
    elif spidername == 'weibo':
        spider_class = WeiboSpider
    elif spidername == 'baidu':
        spider_class = BaiduSpider
    elif spidername == 'baidunews':
        spider_class = BaidunewsSpider
    elif spidername == "ss_360":
        spider_class = Ss360Spider
    elif spidername == "ss_360_zx":
        spider_class = Ss360ZZSpider
    elif spidername == "chinaso":
        spider_class = ChinaSoSpider
    elif spidername == "chinaso_news":
        spider_class = ChinaSoNewsSpider
    else:
        return []

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(dict(item))

    dispatcher.connect(crawler_results, signal=signals.item_passed)

    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_class, keywords=keywords,
                  pagenum=pagenum, sorttype=sorttype)
    process.start()  # the script will block here until the crawling is finished
    return json.dumps(results, ensure_ascii=False).encode('gbk', 'ignore').decode('gbk')


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        spidername = sys.argv[1]
        keywords = sys.argv[2]
        pagenum = int(sys.argv[3])
        sorttype = 1 if len(sys.argv) == 4 else sys.argv[4]
        if keywords:
            if pagenum <= 0:
                pagenum = 1
            searchresult = spider_results(
                spidername, keywords, pagenum, sorttype)
            print(searchresult)
