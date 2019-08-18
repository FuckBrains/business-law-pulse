# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def solton_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//a[@class="newtitle"]/..'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a//text()').extract()[0].strip()

        time_str = record.xpath('./span//text()').extract()[0][1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def solton_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="content mt30 mb40"]')
    item['content'] = ''.join(content.xpath('./div[3]//text()').extract()).strip()

    yield item




class Solton_1_Spider(NewsSpider):
    name = 'solton_1'

    action = {
        'entry': solton_entry_1,
        'fetch': solton_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.solton.com.cn/cn/news.asp?sortid=76&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,6)]))

        tpl = 'http://www.solton.com.cn/cn/news.asp?sortid=3&page=%s'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,6)]))

        super(Solton_1_Spider,self).__init__(*args, **kwargs)




