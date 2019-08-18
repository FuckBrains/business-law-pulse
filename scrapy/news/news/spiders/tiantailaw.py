# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def tiantailaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="newlist"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a/@title').extract()[0].strip()

        time_str = record.xpath('./span/text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def tiantailaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="conts"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class TianTaiLaw_1_Spider(NewsSpider):
    name = 'tiantailaw_1'

    action = {
        'entry': tiantailaw_entry_1,
        'fetch': tiantailaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.tiantailaw.com/information/business.html'
        self.config.update(dict([(tpl,'交易')]))

        tpl = 'http://www.tiantailaw.com/information/business_%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(2,5)]))

        tpl = 'http://www.tiantailaw.com/information/index.html'
        self.config.update(dict([(tpl,'新闻')]))

        tpl = 'http://www.tiantailaw.com/information/index_%s.html'
        self.config.update(dict([(tpl % i,'新闻') for i in range(2,38)]))

        super(TianTaiLaw_1_Spider,self).__init__(*args, **kwargs)




