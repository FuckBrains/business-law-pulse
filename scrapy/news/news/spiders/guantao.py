# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def guantao_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//div[@class="news_text"]/a'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = record.xpath('.//text()').extract()[0].strip()

        time_str = record.xpath('./following-sibling::font[1]/text()').extract()[0]
        item['published'] = utils.parse_publish_time(time_str)

        url = record.xpath('./@href').extract()[0].strip()
        url = urljoin(response.url,url)

        yield scrapy.Request(url, callback=fetch, meta={ 'item': item }, dont_filter=True)




def guantao_fetch(response):
    selector = scrapy.Selector(response=response)
    item = response.meta['item']
    item['url'] = response.url

    content = selector.xpath('//div[@class="news_article_content"]')
    item['content'] = ''.join(content.xpath('.//text()').extract()).strip()

    yield item




class GuanTao_1_Spider(NewsSpider):
    name = 'guantao_1'

    action = {
        'entry': guantao_entry_1,
        'fetch': guantao_fetch,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.guantao.com/html/gtxinewn/list_504_%s.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(1,18)]))

        super(GuanTao_1_Spider,self).__init__(*args, **kwargs)




