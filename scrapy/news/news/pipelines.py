# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.conf import settings
from mongoengine import Q

import os,sys,json,datetime,time
import re,random
from urllib.parse import urlparse

from news import utils
from news.models import CrawlArticle



class ValidateItemPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        parser = urlparse(item['url'])
        if not parser.query and parser.path in ('','/'):
            print('########## INVALIDURL ##########')
            print(json.dumps(item.digest(),ensure_ascii=False))
            raise DropItem('Invalid url')

        if not item.get('published',None):
            print('########## EMPTYTIME ##########')
            print(json.dumps(item.digest(),ensure_ascii=False))
            raise DropItem('Empty published time')

        """
        if utils.is_future_time(item['published']):
            print('########## FUTURETIME ##########')
            print(json.dumps(item.digest(),ensure_ascii=False))
            raise DropItem('Future published time')
        """

        return item



class NewsPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        tag = spider.config[item['entry']]

        article = CrawlArticle.objects.filter(website=spider.website,url=item['url']).first()
        if article:
            article.title = item['title']
            article.save()

            if tag in article.tags:
                raise DropItem('Duplicate news')
            else:
                article.tags.append(tag)
                article.save()
                return item

        article = CrawlArticle.objects.filter(website=spider.website,title=item['title']).first()
        if article:
            if tag in article.tags:
                raise DropItem('Duplicate news')
            else:
                article.tags.append(tag)
                article.save()
                return item

        article = CrawlArticle()
        article.website = spider.website
        article.tags.append(tag)
        article.url = item['url']
        article.title = item['title']
        article.published = item['published'] + datetime.timedelta(microseconds=datetime.datetime.now().microsecond)
        article.content = item['content']
        article.summary = item.get('summary','') or re.sub('(\s|\n|(&nbsp;))+',' ',item['content'])[:100]

        random.seed(time.time())
        article.view = random.randint(100,200)
        article.reply = random.randint(50,150)

        article.crawled = datetime.datetime.now()
        article.save()

        return item



