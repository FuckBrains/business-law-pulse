# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def grandall_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@class="newlist newlist3"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a//text()').extract()[0].strip()

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def grandall_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    time_str = selector.xpath('.//span[@class="newico"]/text()').extract()[0]
    time_str += '-' + selector.xpath('.//span[@class="newico"]/code/text()').extract()[0]
    item['published'] = utils.parse_publish_time(time_str)

    content = selector.xpath('//div[@class="article"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class GrandAll_1_Spider(NewsSpider):
    name = 'grandall_1'

    action = {
        'entry': grandall_entry_1,
        'fetch': grandall_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.grandall.com.cn/xinwen.aspx?column=zxyj&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,45)]))

        tpl = 'http://www.grandall.com.cn/xinwen.aspx?column=press-releases&page=%s'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,32)]))

        super(GrandAll_1_Spider,self).__init__(*args, **kwargs)




