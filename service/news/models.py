# -*- coding: utf-8 -*-

from core.conf import CONST

import os,sys,datetime,time,json
import mongoengine



class EditNewsArticle(mongoengine.Document):
    tags = mongoengine.ListField(default=[])                # 标签
    cover = mongoengine.DictField(default=None)             # 封面
    title = mongoengine.StringField(default='')             # 标题
    summary = mongoengine.StringField(default='')           # 摘要
    content = mongoengine.StringField(default='')           # 正文
    tags = mongoengine.ListField(default=[])                # 标签
    view = mongoengine.IntField(default=0)                  # 阅读数
    reply = mongoengine.IntField(default=0)                 # 评论数

    status = mongoengine.IntField(default=1)                # 新闻状态（0-删除，1-正常）
    published = mongoengine.DateTimeField(default=None)     # 发表时间
    created = mongoengine.DateTimeField(default=datetime.datetime.now())
    updated = mongoengine.DateTimeField(default=datetime.datetime.now())


    meta = {'db_alias': 'edit', 'collection': 'edit_news_article',
            'indexes': ['published', 'created'],
            'auto_create_index': False}

    def digest(self):
        return {
            'id': str(self.id),
            'cover': self.cover,
            'source': '足球地带',
            'tags': self.tags,
            'title': self.title,
            'summary': self.summary,
            'view': self.view,
            'reply': self.reply,

            'url': '%s://%s/news/share?type=edit&id=%s&download=1' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),

            'status': self.status,
            'published': int(self.published.timestamp()*1000),
            'created': int(self.created.timestamp()*1000),
        }

    def detail(self):
        return {
            'id': str(self.id),
            'cover': self.cover,
            'source': '足球地带',
            'tags': self.tags,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'view': self.view,
            'reply': self.reply,

            'url': '%s://%s/news/share?type=edit&id=%s&download=1' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),
            'hybrid': '%s://%s/news/hybrid?type=edit&id=%s' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),
            'fake': '%s://%s/news/fake?type=edit&id=%s' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),

            'status': self.status,
            'published': int(self.published.timestamp()*1000),
            'created': int(self.created.timestamp()*1000),

            'share': {
                'title': self.title,
                'summary': self.summary,
                #'image': self.cover['thumbnails'][0]['url'],
                'url': '%s://%s/news/share?type=edit&id=%s&download=1' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),
            },
        }


class EmbeddedDtagInfo(mongoengine.EmbeddedDocument):
    title = mongoengine.StringField(default='')             # 重复新闻标题
    url = mongoengine.StringField(default='')               # 重复新闻链接
    words = mongoengine.ListField(default=[])               # 重复关键词


class CrawlNewsArticle(mongoengine.Document):
    website = mongoengine.StringField(default='')           # 爬虫网站
    source = mongoengine.StringField(default='')            # 来源
    tags = mongoengine.ListField(default=[])                # 标签

    url = mongoengine.StringField(default='')               # 新闻页面URL
    cover = mongoengine.DictField(default=None)             # 封面
    title = mongoengine.StringField(default='')             # 标题
    summary = mongoengine.StringField(default='')           # 摘要
    content = mongoengine.StringField(default='')           # 正文
    view = mongoengine.IntField(default=0)                  # 阅读数
    reply = mongoengine.IntField(default=0)                 # 评论数

    dtags = mongoengine.ListField(default=[])               # 在list标签下重复
    dinfo = mongoengine.DictField(default={})               # 在dict对应标签下重复的信息

    status = mongoengine.IntField(default=1)                # 新闻状态（0-删除，1-正常）
    published = mongoengine.DateTimeField(default=None)     # 新闻发表时间
    crawled = mongoengine.DateTimeField(default=None)       # 新闻爬取时间

    meta = {'db_alias': 'crawl', 'collection': 'crawl_news_article',
            'indexes': ['published', 'crawled'],
            'auto_create_index': False}

    def digest(self):
        return {
            'id': str(self.id),
            'website': self.website,
            'source': self.source,
            'tags': self.tags,
            'cover': self.cover,
            'title': self.title,
            'summary': self.summary,
            'view': self.view,
            'reply': self.reply,
            'status': self.status,
            'published': int(self.published.timestamp()*1000),
            'crawled': int(self.crawled.timestamp()*1000),
            'dtags': self.dtags,
            'dinfo': self.dinfo,

            'url': self.url,
        }

    def detail(self):
        return {
            'id': str(self.id),
            'website': self.website,
            'source': self.source,
            'tags': self.tags,
            'cover': self.cover,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'view': self.view,
            'reply': self.reply,
            'dtags': self.dtags,
            'dinfo': self.dinfo,

            'url': self.url,
            'fake': '%s://%s/news/fake?type=crawl&id=%s' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),

            'status': self.status,
            'published': int(self.published.timestamp()*1000),
            'crawled': int(self.crawled.timestamp()*1000),

            'share': {
                'title': self.title,
                'summary': self.summary,
                #'image': self.cover['thumbnails'][0]['url'] if self.cover else (CONST['static']['url']+'images/index/share_icon.jpg'),
                'url': '%s://%s/news/share?type=crawl&id=%s&download=1' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),
            },
        }


class CrawlSpiderStats(mongoengine.Document):
    website = mongoengine.StringField()
    tag = mongoengine.StringField()
    entry = mongoengine.StringField()

    scraped = mongoengine.IntField(default=0)
    dropped = mongoengine.IntField(default=0)
    dumplicated = mongoengine.IntField(default=0)

    start = mongoengine.DateTimeField()
    end = mongoengine.DateTimeField()
    spider = mongoengine.StringField()

    classes = mongoengine.StringField(default="")

    meta = {'db_alias': 'crawl', 'collection': 'crawl_spider_stats'}

    def detail(self):
        return {
            'website': self.website,
            'tag': self.tag,
            'entry': self.entry,

            'scraped': self.scraped,
            'dropped': self.dropped,

            'start': int(self.start.timestamp()*1000),
            'end': int(self.end.timestamp()*1000),
            'spider': self.spider,
        }


