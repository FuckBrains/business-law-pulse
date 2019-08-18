# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.conf import settings

import os,sys,json,datetime,time,re
from urllib.parse import urljoin,urlparse

from news import utils
from news.spiders import NewsSpider
from news.items import NewsItem




def jiayuan_entry_1(response, fetch):
    selector = scrapy.Selector(response=response)

    for record in selector.xpath('//span[@class="style47"]/../../../../../../..'):
        item = NewsItem()
        item['entry'] = response.url

        item['title'] = ''.join(record.xpath('.//span[@class="style47"]/../strong//text()').extract()).strip()
        item['content'] = ''.join(record.xpath('./table[2]//text()').extract())

        time_str = item['title'].split('|')[-1].strip()
        item['published'] = utils.parse_publish_time(time_str)

        if record.xpath('./table[2]//a'):
            item['url'] = record.xpath('./table[2]//a/@href').extract()[0]
        else:
            item['url'] = response.url + '#' + item['published'].strftime('%Y%m%d')

        yield item




class JiaYuan_1_Spider(NewsSpider):
    name = 'jiayuan_1'

    action = {
        'entry': jiayuan_entry_1,
        'fetch': None,
    }

    def __init__(self, *args, **kwargs):
        tpl = 'http://www.jiayuan-law.com/cn/news/news-cn.html'
        self.config.update(dict([(tpl,'交易')]))

        tpl = 'http://www.jiayuan-law.com/cn/news/%s-news-cn.html'
        self.config.update(dict([(tpl % i,'交易') for i in range(2011,2016)]))

        tpl = 'http://www.jiayuan-law.com/cn/news/old-news-cn.html'
        self.config.update(dict([(tpl,'交易')]))

        super(JiaYuan_1_Spider,self).__init__(*args, **kwargs)




