# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def zhonglun_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@class="titlelist2"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/text()').extract()[0].strip()

        time_str = record.xpath('./span[2]//text()').extract()[0][1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def zhonglun_entry_2(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//table[@class="contentDetail"]'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//span[@class="contentTitle"]//a/text()').extract()[0].strip()
        if not item['title']:
            continue

        time_str = ''.join(record.xpath('.//span[@class="dateColor"]//text()').extract())[1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//span[@class="contentTitle"]//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def zhonglun_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="lh22"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class ZhongLun_1_Spider(NewsSpider):
    name = 'zhonglun_1'

    action = {
        'entry': zhonglun_entry_1,
        'fetch': zhonglun_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.zhonglun.com/Cn/WebPage_4_15_%s.aspx'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,42)]))

        tpl = 'http://www.zhonglun.com/Cn/WebPage_4_14_%s.aspx'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,64)]))

        tpl = 'http://www.zhonglun.com/cn/WebPage_25.aspx'
        self.config.update(dict([(tpl,'新闻')]))

        super(ZhongLun_1_Spider,self).__init__(*args, **kwargs)




class ZhongLun_2_Spider(NewsSpider):
    name = 'zhonglun_2'

    action = {
        'entry': zhonglun_entry_2,
        'fetch': zhonglun_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.zhonglun.com/Cn/WebPage_4_29_%s.aspx'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,3)]))

        super(ZhongLun_2_Spider,self).__init__(*args, **kwargs)




