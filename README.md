## searchengine
## 一个搜索引擎  
#### 1 python3
#### 2 scrapy
```pip3 install scrapy```
#### 3 使用方法
```
git clone https://github.com/zhu733756/searchengine.git
cd searchengine [search.py的父目录]
python3 search.py [site] [keywords] [page] [sorttype]
```
#####	site: 目前支持 bing/weibo/weixin/baidu/baidunews/ss_360/ss_360_zx/chinaso/chinaso_news 之一
#####	keywords: 关键词，多个用+连接
#####	page: 页码
#####	sorttype: baidunews支持 1-按照焦点排序，4-按时间排序
#####	输出结果以打印成json数据输出在终端
