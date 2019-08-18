# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def hylandslaw_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="li_con"]'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./h2/a//text()').extract()[0].strip()

        time_str = record.xpath('./h2/span//text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        item['summary'] = record.xpath('./p//text()').extract()[0]

        url = record.xpath('./h2/a/@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def hylandslaw_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="article"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class HylandsLaw_1_Spider(NewsSpider):
    name = 'hylandslaw_1'

    action = {
        'entry': hylandslaw_entry_1,
        'fetch': hylandslaw_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.hylandslaw.com/newscenter/zuixinjiaoyi/?year=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(2011,2016)]))

        tpl = 'http://www.hylandslaw.com/newscenter/news.html?page=%s'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,7)]))

        super(HylandsLaw_1_Spider,self).__init__(*args, **kwargs)




