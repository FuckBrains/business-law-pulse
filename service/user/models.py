# -*- coding: utf-8 -*-

import mongoengine




class User(mongoengine.Document):
    TYPE_CHOICES = (
        (0,'马甲'),
        (1,'普通'),
    )

    GENDER_CHOICES = (
        ('','保密'),
        ('M','男'),
        ('F','女'),
    )

    STATUS_CHOICES = (
        (-1,'已屏蔽'),
        (0,'已删除'),
        (1,'正常'),
        (2,'未激活'),
        (3,'已禁言'),
    )

    type = mongoengine.IntField(default=1,choices=TYPE_CHOICES)                 # 类型
    password = mongoengine.StringField(default=None)                            # 密码（MD5）

    avatar = mongoengine.DictField(default={})                                  # 头像
    nickname = mongoengine.StringField(max_length=32,required=True)             # 昵称
    gender = mongoengine.StringField(max_length=1,choices=GENDER_CHOICES)       # 性别
    province = mongoengine.DictField(default=None)                              # 省份
    city = mongoengine.DictField(default=None)                                  # 城市

    cellphone = mongoengine.StringField(max_length=32,default='')               # 手机
    email = mongoengine.StringField(max_length=128,default='')                  # 邮箱
    qq = mongoengine.StringField(max_length=16,default='')                      # ＱＱ
    weixin = mongoengine.StringField(default='')                                # 微信
    weibo = mongoengine.StringField(default='')                                 # 微博

    qq_openid = mongoengine.StringField(default='')                             # ＱＱ第三方登录OpenID
    weixin_openid = mongoengine.StringField(default='')                         # 微信第三方登录OpenID
    weixin_unionid = mongoengine.StringField(default='')                        # 微信第三方登录UnionID

    device_agent = mongoengine.StringField(default='')                          # 最近登录设备Agent
    device_token = mongoengine.StringField(default='')                          # 最近登录设备Token

    permissions = mongoengine.ListField(default=[])                             # 权限

    status = mongoengine.IntField(choices=STATUS_CHOICES,default=1)
    created = mongoengine.DateTimeField()
    updated = mongoengine.DateTimeField()

    meta = { 'db_alias': 'default', 'collection': 'user' }

    def digest(self):
        return {
            'id': str(self.id),
            'type': self.type,
            'avatar': self.avatar,
            'nickname': self.nickname,
            'gender': self.gender,
            'province': self.province,
            'city': self.city,
            'status': self.status,
            'created': int(self.created.timestamp()*1000),
        }

    def detail(self):
        return {
            'id': str(self.id),
            'sid': self.sid,
            'avatar': self.avatar,
            'nickname': self.nickname,
            'gender': self.gender,
            'province': self.province,
            'city': self.city,
            'cellphone': self.cellphone,
            'email': self.email,
            'qq': self.qq,
            'weixin': self.weixin,
            'weibo': self.weibo,

            'qq_openid': self.qq_openid,
            'weixin_openid': self.weixin_openid,
            'weixin_unionid': self.weixin_unionid,

            'permissions': self.permissions,
            'status': self.status,
            'created': int(self.created.timestamp()*1000),
        }


