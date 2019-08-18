# -*- coding: utf-8 -*-

import mongoengine



class Admin(mongoengine.Document):
    GENDER_CHOICES = (
        ('','保密'),
        ('M','男'),
        ('F','女'),
    )

    STATUS_CHOICES = (
        (0,'已删除'),
        (1,'正常'),
    )

    realname = mongoengine.StringField(default='')                                      # 真实姓名
    gender = mongoengine.StringField(max_length=1,choices=GENDER_CHOICES)               # 性别
    avatar = mongoengine.DictField(default=None)                                        # 头像

    cellphone = mongoengine.StringField(default='')                                     # 手机
    email = mongoengine.StringField(default='')                                         # 邮箱
    password = mongoengine.StringField(default=None)                                    # 密码（MD5）

    remark = mongoengine.StringField(default='')                                        # 备注
    permissions = mongoengine.ListField(default=[])                                     # 权限

    status = mongoengine.IntField(choices=STATUS_CHOICES,default=1)
    created = mongoengine.DateTimeField()
    updated = mongoengine.DateTimeField()

    meta = { 'db_alias': 'default', 'collection': 'admin' }

    def digest(self):
        return {
            'id': str(self.id),
            'avatar': self.avatar,
            'realname': self.realname,
            'gender': self.gender,
            'cellphone': self.cellphone,
            'email': self.email,
            'status': self.status,
        }

    def detail(self):
        return {
            'id': str(self.id),
            'avatar': self.avatar,
            'realname': self.realname,
            'gender': self.gender,
            'cellphone': self.cellphone,
            'email': self.email,
            'remark': self.remark,
            'permissions': self.permissions,
            'status': self.status,
            'created': int(self.created.timestamp()*1000),
        }



