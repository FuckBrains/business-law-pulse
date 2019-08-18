# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def deheng_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="m-artice-list"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a//text()').extract()[0].strip()

        time_str = record.xpath('./span//text()').extract()[0][1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def deheng_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="m-artice-a"]')
    item['content'] = ''.join(content.xpath('./*[not(@class="tit") and not(@class="hd")]//text() | ./text()').extract()).strip()

    yield item




class DeHeng_1_Spider(NewsSpider):
    name = 'deheng_1'

    action = {
        'entry': deheng_entry_1,
        'fetch': deheng_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.deheng.com.cn/more/?typeindex=syzxal&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,6)]))

        super(DeHeng_1_Spider,self).__init__(*args, **kwargs)




