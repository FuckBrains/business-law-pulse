# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def huashang_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//a[@class="f12"]/..'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a/text()').extract()[0].strip()

        time_str = record.xpath('./font/text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def huashang_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="f14" and contains(@style,"overflow")]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class HuaShang_1_Spider(NewsSpider):
    name = 'huashang_1'

    action = {
        'entry': huashang_entry_1,
        'fetch': huashang_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.huashang.cn/newslist.asp?cid=109&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,5)]))

        tpl = 'http://www.huashang.cn/newslist.asp?cid=108&page=%s'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,15)]))

        super(HuaShang_1_Spider,self).__init__(*args, **kwargs)




