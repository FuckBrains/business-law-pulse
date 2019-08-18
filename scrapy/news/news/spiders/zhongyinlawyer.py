# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def zhongyinlawyer_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="list_news font_a"]//a'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('./text()').extract()[0].strip()

        time_str = record.xpath('./span[@class="floatR"]/text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def zhongyinlawyer_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="news_con editing"]')
    item['content'] = ''.join(content.xpath('./*[name() != "h2" and name() != "h3"]//text() | ./text()').extract()).strip()

    yield item




class ZhongYinLawyer_1_Spider(NewsSpider):
    name = 'zhongyinlawyer_1'

    action = {
        'entry': zhongyinlawyer_entry_1,
        'fetch': zhongyinlawyer_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.zhongyinlawyer.com/news.aspx?t=3&page=%s'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,25)]))

        tpl = 'http://www.zhongyinlawyer.com/news.aspx?t=4&page=%s'
        self.config.update(dict([(tpl % i,'新闻') for i in range(1,38)]))

        super(ZhongYinLawyer_1_Spider,self).__init__(*args, **kwargs)




