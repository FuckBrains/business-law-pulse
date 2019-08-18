# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def tahota_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//ul[@class="news-list"]/li'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//h3/a//text()').extract()[0].strip()

        time_str = record.xpath('.//em/text()').extract()[0].strip() + '.' + record.xpath('./span/text()').extract()[0].strip()
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('.//h3/a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def tahota_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="l-article"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class TaHoTa_1_Spider(NewsSpider):
    name = 'tahota_1'

    action = {
        'entry': tahota_entry_1,
        'fetch': tahota_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.tahota-lawyer.com/cn/act.php?id=471&cid=513&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,17)]))

        tpl = 'http://www.tahota-lawyer.com/cn/news.php?id=471&cid=476&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,106)]))

        super(TaHoTa_1_Spider,self).__init__(*args, **kwargs)




