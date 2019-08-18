# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def haiwen_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="lawyer_right"]//a'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./text()').extract()[0].strip()

        time_str = ''.join(record.xpath('../text()').extract())[1:-1]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def haiwen_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="lawyer_right"]')
    item['content'] = ''.join(content.xpath('./*[not(@class="fontcolor")]//text() | ./text()').extract()).strip()

    yield item




class HaiWen_1_Spider(NewsSpider):
    name = 'haiwen_1'

    action = {
        'entry': haiwen_entry_1,
        'fetch': haiwen_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.haiwen-law.com/plus/list.php~tid=24.html'
        self.config.update(dict([(tpl,'交易')]))

        super(HaiWen_1_Spider,self).__init__(*args, **kwargs)




