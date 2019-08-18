# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def anjielaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="newstitle"]'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/@title').extract()[0].strip()

        time_str = ''.join(record.xpath('.//li[@class="date"]//text()').extract()).strip()
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def anjielaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@id="infoContent"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class AnJieLaw_1_Spider(NewsSpider):
    name = 'anjielaw_1'

    action = {
        'entry': anjielaw_entry_1,
        'fetch': anjielaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.anjielaw.com/news_list/&newsCategoryId=12&FrontNews_list01-1349947321158_pageNo=%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,14)]))

        super(AnJieLaw_1_Spider,self).__init__(*args, **kwargs)




