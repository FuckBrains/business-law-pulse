# -*- coding: utf-8 -*-

from core.conf import CONST

import datetime
import mongoengine


class InfoVideo(mongoengine.Document):
    MODE_CHOICES = (
        (1,'原生播放器'),
        (2,'内置浏览器'),
        (3,'系统浏览器'),
    )

    title = mongoengine.StringField(default='')                                         # 标题
    cover = mongoengine.DictField(default=None)                                         # 封面
    description = mongoengine.StringField(default='')                                   # 描述

    tags = mongoengine.ListField(default=[])                                            # 标签
    duration = mongoengine.IntField(default=0)                                          # 播放时长
    schedule = mongoengine.StringField(default='')                                      # 关联赛程

    view = mongoengine.IntField(default=0)                                              # 播放数
    reply = mongoengine.IntField(default=0)                                             # 评论数

    mode = mongoengine.IntField(choices=MODE_CHOICES,default=1)                         # 播放模式
    reference = mongoengine.StringField(default='')                                     # 参考页面URL
    url = mongoengine.StringField(default='')                                           # 视频页面URL
    stream = mongoengine.StringField(default='')                                        # 视频流URL

    status = mongoengine.IntField(default=1)
    created = mongoengine.DateTimeField(default=datetime.datetime.now())
    updated = mongoengine.DateTimeField(default=datetime.datetime.now())

    meta = { 'db_alias': 'default', 'collection': 'info_video',
            'indexes': ['created','updated'],
            'auto_create_index': False }

    def digest(self):
        return {
            'id': str(self.id),
            'tags': self.tags,
            'title': self.title,
            'cover': self.cover,
            'description': self.description,
            'duration': self.duration,
            'schedule': self.schedule,
            'view': self.view,
            'reply': self.reply,

            'mode': self.mode,
            'reference': self.reference,
            'url': self.url,
            'stream': self.stream,
            'created': int(self.created.timestamp()*1000),
        }

    def detail(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'cover': self.cover,
            'description': self.description,
            'duration': self.duration,
            'schedule': self.schedule,
            'tags': self.tags,
            'view': self.view,
            'reply': self.reply,

            'mode': self.mode,
            'reference': self.reference,
            'url': self.url,
            'stream': self.stream,
            'created': int(self.created.timestamp()*1000),

            'hybrid': '%s://%s/video/%s/?type=hybrid' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)),

            'share': {
                'title': self.title,
                'summary': self.description,
                'image': self.cover.thumbnails[0].url,
                'url': '%s://%s/video/%s/?download=1' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'], str(self.id)) if self.mode == 1 else self.url,
            },
        }
