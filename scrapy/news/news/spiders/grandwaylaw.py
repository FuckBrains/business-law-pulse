# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def grandwaylaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="xwzx"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a//text()').extract()[0].strip()

        time_str = record.xpath('./span//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def grandwaylaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="txt"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class GrandWayLaw_1_Spider(NewsSpider):
    name = 'grandwaylaw_1'

    action = {
        'entry': grandwaylaw_entry_1,
        'fetch': grandwaylaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.grandwaylaw.com/cn/news/latestresults.html'
        self.config.update(dict([(tpl,'交易')]))

        tpl = 'http://www.grandwaylaw.com/cn/news/latestresults_%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(2,21)]))

        tpl = 'http://www.grandwaylaw.com/cn/news/firmnews.html'
        self.config.update(dict([(tpl,'新闻')]))

        tpl = 'http://www.grandwaylaw.com/cn/news/firmnews_%s.html'
        self.config.update(dict([(tpl % i,'新闻') for i in range(2,8)]))

        super(GrandWayLaw_1_Spider,self).__init__(*args, **kwargs)




