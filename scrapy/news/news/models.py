# -*- coding: utf-8 -*-

import sys,os,json
import mongoengine



class EmbeddedImage(mongoengine.EmbeddedDocument):
    id = mongoengine.StringField(default='')
    name = mongoengine.StringField(default='')
    path = mongoengine.StringField(default='')
    scene = mongoengine.StringField(default='')
    type = mongoengine.StringField(default='')
    size = mongoengine.IntField(default=0)
    width = mongoengine.IntField(default=0)
    height = mongoengine.IntField(default=0)
    thumbnails = mongoengine.EmbeddedDocumentListField('EmbeddedThumbnail',default=[])
    created = mongoengine.DateTimeField(default=None)



class EmbeddedThumbnail(mongoengine.EmbeddedDocument):
    width = mongoengine.IntField(default=0)
    height = mongoengine.IntField(default=0)
    path = mongoengine.StringField(default='')



class CrawlArticle(mongoengine.Document):
    STATUS_CHOICES = (
        (1,'未处理'),
        (2,'已处理'),
    )

    website = mongoengine.StringField()
    tags = mongoengine.ListField(default=[])

    url = mongoengine.StringField()
    title = mongoengine.StringField()

    summary = mongoengine.StringField()
    content = mongoengine.StringField()

    status = mongoengine.IntField(choices=STATUS_CHOICES,default=1)
    published = mongoengine.DateTimeField()
    crawled = mongoengine.DateTimeField()

    meta = { 'db_alias': 'crawl-primary', 'collection': 'crawl_article', 'indexes': ['published','crawled'] }




class CrawlArticleStats(mongoengine.Document):
    website = mongoengine.StringField()
    tag = mongoengine.StringField()
    entry = mongoengine.StringField()

    scraped = mongoengine.IntField(default=0)
    dropped = mongoengine.IntField(default=0)

    start = mongoengine.DateTimeField()
    end = mongoengine.DateTimeField()
    spider = mongoengine.StringField()

    meta = { 'db_alias': 'crawl-primary', 'collection': 'crawl_article_stats' }




