# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def coeffort_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="news_show"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//p[@class="news_info_title"]/a/text()').extract()[0].strip()

        time_str = record.xpath('./p[@class="dateTime"]//text()').extract()[-1].strip()
        time_str += '/'
        time_str += record.xpath('./p[@class="dateTime"]//text()').extract()[0].strip()
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def coeffort_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="news_view_info"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class CoEffort_1_Spider(NewsSpider):
    name = 'coeffort_1'

    action = {
        'entry': coeffort_entry_1,
        'fetch': coeffort_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=20&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,6)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=237&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,7)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=39&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,23)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=41&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,24)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=47&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,10)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=48&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,3)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=49&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,6)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=50&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,6)]))

        tpl = 'http://www.co-effort.com/index.php?m=content&c=index&a=lists&catid=51&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,5)]))

        super(CoEffort_1_Spider,self).__init__(*args, **kwargs)




