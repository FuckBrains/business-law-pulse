# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def zhonglunwende_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@class="z_news_ul"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./a/text()').extract()[0].strip()

        time_str = record.xpath('./span/text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def zhonglunwende_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="neiRong_text"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class ZhongLunWenDe_1_Spider(NewsSpider):
    name = 'zhonglunwende_1'

    action = {
        'entry': zhonglunwende_entry_1,
        'fetch': zhonglunwende_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.zhonglunwende.com/index.php/List/law/id/157?&p=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,89)]))

        super(ZhongLunWenDe_1_Spider,self).__init__(*args, **kwargs)




