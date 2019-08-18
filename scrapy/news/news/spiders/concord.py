# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def concord_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@id="latest_list"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//a/text()').extract()[0].strip()

        time_str = record.xpath('./div[@class="date"]//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def concord_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@id="latest_detail_content"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class Concord_1_Spider(NewsSpider):
    name = 'concord_1'

    action = {
        'entry': concord_entry_1,
        'fetch': concord_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.east-concord.com/news.php?id=1&pageNum=%s'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,13)]))

        super(Concord_1_Spider,self).__init__(*args, **kwargs)




