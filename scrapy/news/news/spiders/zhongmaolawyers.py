# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def zhongmaolawyers_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//table[@width="666"]')[1].xpath('.//table[1]//a/../..'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/text()').extract()[0].strip()

        time_str = record.xpath('./td[2]/text()').extract()[0][1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def zhongmaolawyers_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//table[@width="666"]')[1]
    item['content'] = ''.join(content.xpath('./tr[5]//text()').extract()).strip()

    yield item




class ZhongMaoLawyers_1_Spider(NewsSpider):
    name = 'zhongmaolawyers_1'

    action = {
        'entry': zhongmaolawyers_entry_1,
        'fetch': zhongmaolawyers_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.zhongmaolawyers.com/cn/news.asp?sortid=29&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,11)]))

        tpl = 'http://www.zhongmaolawyers.com/cn/news.asp?sortid=8&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,33)]))

        super(ZhongMaoLawyers_1_Spider,self).__init__(*args, **kwargs)




