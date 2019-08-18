# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def glo_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@class="news-list lsn"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/@title').extract()[0].strip()

        time_str = record.xpath('.//time//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def glo_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//article/*[not(@class="heading2")]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class GLO_1_Spider(NewsSpider):
    name = 'glo_1'

    action = {
        'entry': glo_entry_1,
        'fetch': glo_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.glo.com.cn/news/news_list.html'
        self.config.update(dict([(tpl,'交易')]))

        tpl = 'http://www.glo.com.cn/news/news_list_%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(2,32)]))

        super(GLO_1_Spider,self).__init__(*args, **kwargs)




