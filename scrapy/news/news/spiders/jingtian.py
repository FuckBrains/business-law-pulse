# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def jingtian_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="node_list"]'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/@title').extract()[0].strip()

        time_str = record.xpath('.//span[@class="time1"]//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def jingtian_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="news_c_c"]')
    item['content'] = ''.join(content.xpath('./*[name() != "h2"]//text() | ./text()').extract()).strip()

    yield item




class JingTian_1_Spider(NewsSpider):
    name = 'jingtian_1'

    action = {
        'entry': jingtian_entry_1,
        'fetch': jingtian_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.jingtian.com/zh-hans/taxonomy/term/11?page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(0,13)]))

        tpl = 'http://www.jingtian.com/zh-hans/taxonomy/term/70?page=0'
        self.config.update(dict([(tpl % i,'新闻') for i in range(0,2)]))

        super(JingTian_1_Spider,self).__init__(*args, **kwargs)




