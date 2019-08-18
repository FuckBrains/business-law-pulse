# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def gslaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="xwzx-center-right-2"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/@title').extract()[0].strip()

        time_str = record.xpath('./div[2]//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def gslaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@style="padding:5px;"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class GSLaw_1_Spider(NewsSpider):
    name = 'gslaw_1'

    action = {
        'entry': gslaw_entry_1,
        'fetch': gslaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.gslaw.com.cn/cn/list/iedubbjbkhcmckcjj/%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,5)]))

        tpl = 'http://www.gslaw.com.cn/cn/list/iegubbjbmfcmckhjg/%s.html'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,5)]))

        super(GSLaw_1_Spider,self).__init__(*args, **kwargs)




