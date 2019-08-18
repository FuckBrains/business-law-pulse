# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def dachenglaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="m-news-list"]/dl'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/@title').extract()[0].strip()

        time_str = record.xpath('.//dd[@class="u-date"]//text()').extract()[0].strip()
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = url[:url.find('.html')+5]
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def dachenglaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="m-article-content"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class DaChangLaw_1_Spider(NewsSpider):
    name = 'dachenglaw_1'

    action = {
        'entry': dachenglaw_entry_1,
        'fetch': dachenglaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.dachenglaw.com/cn/news/recent?currentPageNo=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,176)]))

        super(DaChangLaw_1_Spider,self).__init__(*args, **kwargs)




