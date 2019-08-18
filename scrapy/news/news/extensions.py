# -*- coding: utf-8 -*-

from scrapy.conf import settings
from scrapy import signals
from scrapy.exceptions import NotConfigured

import os,sys,json,datetime,time

from news.models import CrawlArticleStats

import logging
logger = logging.getLogger(__name__)


#http://doc.scrapy.org/en/latest/topics/extensions.html
class ExportStats(object):

    def __init__(self, stats):
        self.stats = stats
        self.result = {}


    @classmethod
    def from_crawler(cls, crawler):
        # instantiate the extension object
        ext = cls(crawler.stats)

        # connect the extension object to signals
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        # return the extension object
        return ext


    def spider_opened(self, spider):
        spider.error = 0


    def spider_closed(self, spider):
        # news stats
        for tag in self.result:
            stats = CrawlArticleStats.objects.filter(website=spider.website,tag=tag).first()
            if not stats:
                stats = CrawlArticleStats()
                stats.website = spider.website
                stats.tag = tag
                stats.entry = self.result[tag]['entry']

            stats.spider = spider.name
            stats.scraped = len(self.result[tag]['scraped_items'])
            stats.dropped = len(self.result[tag]['dropped_items'])
            stats.start = self.stats.get_value('start_time')+datetime.timedelta(hours=8)
            stats.end =  self.stats.get_value('finish_time')+datetime.timedelta(hours=8)
            stats.save()


    def item_scraped(self, item, spider):
        _item = { 'title': item['title'], 'url': item['url'] }

        tag = spider.config[item['entry']]
        if tag in self.result:
            self.result[tag]['scraped_items'].append(_item)
        else:
            self.result[tag] = { 'entry': item['entry'], 'scraped_items': [_item], 'dropped_items': [] }


    def item_dropped(self, item, spider):
        _item = { 'title': item['title'], 'url': item['url'] }

        tag = spider.config[item['entry']]
        if tag in self.result:
            self.result[tag]['dropped_items'].append(_item)
        else:
            self.result[tag] = { 'entry': item['entry'], 'scraped_items': [], 'dropped_items': [_item] }




