# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def hiwayslaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@id="laws-text"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a/@title').extract()[0].strip()

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def hiwayslaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    time_str = selector.xpath('//div[@id="title2"]/text()').extract()[0][-11:-1]
    item['published'] = utils.parse_publish_time(time_str)

    content = selector.xpath('//div[@id="news-info"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class HiWaysLaw_1_Spider(NewsSpider):
    name = 'hiwayslaw_1'

    action = {
        'entry': hiwayslaw_entry_1,
        'fetch': hiwayslaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.hiwayslaw.com/catalog/62d5cc6e761040408f5796c54bdad797?currentPageNo=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,27)]))

        super(HiWaysLaw_1_Spider,self).__init__(*args, **kwargs)




