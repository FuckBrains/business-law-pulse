# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def unitalenlaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//span[@class="9phui"]/..'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a//text()').extract()[0].strip()

        time_str = record.xpath('.//span[@class="9phui"]/span//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def unitalenlaw_entry_2(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@class="lists mt30"]//a/../..'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a//text()').extract()[0].strip()

        time_str = record.xpath('.//span[2]//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0]
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def unitalenlaw_fetch_1(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//span[@id="CurrentlyText"]')
    item['content'] = ''.join(content.xpath('./*[name() != "title"]//text() | ./text()').extract()).strip()

    yield item





def unitalenlaw_fetch_2(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//span[@id="ReportIDtext"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item





class UniTalenLaw_1_Spider(NewsSpider):
    name = 'unitalenlaw_1'

    action = {
        'entry': unitalenlaw_entry_1,
        'fetch': unitalenlaw_fetch_1,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.unitalenlaw.com/html/category/11771-%s.htm'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,11)]))

        tpl = 'http://www.unitalen.com.cn/html/category/10119-%s.htm'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,11)]))

        tpl = 'http://www.unitalenlaw.com/html/category/11771-%s.htm'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,11)]))

        super(UniTalenLaw_1_Spider,self).__init__(*args, **kwargs)




class UniTalenLaw_2_Spider(NewsSpider):
    name = 'unitalenlaw_2'

    action = {
        'entry': unitalenlaw_entry_2,
        'fetch': unitalenlaw_fetch_2,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.unitalenlaw.com/html/category/46558-%s.htm'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,11)]))

        super(UniTalenLaw_2_Spider,self).__init__(*args, **kwargs)




