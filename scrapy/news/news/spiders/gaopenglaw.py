# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def gaopenglaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="newslist"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a/@title').extract()[0].strip()

        time_str = '20' + record.xpath('./span/text()').extract()[0][1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def gaopenglaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="content_text"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class GaoPengLaw_1_Spider(NewsSpider):
    name = 'gaopenglaw_1'

    action = {
        'entry': gaopenglaw_entry_1,
        'fetch': gaopenglaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.gaopenglaw.com/list/?25_%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,28)]))

        super(GaoPengLaw_1_Spider,self).__init__(*args, **kwargs)




