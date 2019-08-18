# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def shujin_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@id="zh_new_lby"]//li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a/text()').extract()[0].strip()

        time_str = record.xpath('./span/text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def shujin_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@id="single"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class ShuJin_1_Spider(NewsSpider):
    name = 'shujin_1'

    action = {
        'entry': shujin_entry_1,
        'fetch': shujin_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.shujin.cn/news.aspx?classid=214'
        self.config.update(dict([(tpl,'新闻')]))

        super(ShuJin_1_Spider,self).__init__(*args, **kwargs)




