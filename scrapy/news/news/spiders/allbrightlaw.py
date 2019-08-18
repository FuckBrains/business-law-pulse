# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def allbrightlaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="xwzx-list"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a//text()').extract()[0].strip()

        time_str = record.xpath('./span//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def allbrightlaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="gailan"]')
    item['content'] = ''.join(content.xpath('./*[name() != "h2" and name() != "h4"]//text()').extract()).strip()

    yield item




class AllBrightLaw_1_Spider(NewsSpider):
    name = 'allbrightlaw_1'

    action = {
        'entry': allbrightlaw_entry_1,
        'fetch': allbrightlaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.allbrightlaw.com/cn/news/transactions?currentPageNo=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,49)]))

        tpl = 'http://www.allbrightlaw.com/cn/news/allbrightnews?currentPageNo=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,26)]))

        super(AllBrightLaw_1_Spider,self).__init__(*args, **kwargs)




