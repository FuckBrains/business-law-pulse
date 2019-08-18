# -*- coding: utf-8 -*-

import os,sys,datetime,time,json

import mongoengine

from core.conf import CONST


class LawConfig(mongoengine.Document):
    key = mongoengine.StringField(default='')
    value = mongoengine.DynamicField(default=None)

    meta = { 'db_alias': 'default', 'collection': 'law_config' }

    def detail(self):
        return {
            'key': self.key,
            'value': self.value,
        }


class LawClient(mongoengine.Document):
    STATUS_CHOICES = (
        (0,'删除'),
        (1,'正常'),
        (2,'注销'),
        (3,'合并'),
    )

    parent = mongoengine.ReferenceField('self',default=None)    # 母公司
    logo = mongoengine.DictField(default=None)

    name = mongoengine.StringField(default='')          # 名称（英文）
    name_cn = mongoengine.StringField(default='')       # 名称（中文）

    industries = mongoengine.ListField(default=[])      # 行业
    area = mongoengine.IntField(default=0)              # 地区

    note = mongoengine.StringField(default='')          # 描述（英文）
    note_cn = mongoengine.StringField(default='')       # 描述（中文）

    raw = mongoengine.StringField(default='')           # 素材

    status = mongoengine.IntField(default=1,choices=STATUS_CHOICES)
    created = mongoengine.DateTimeField(default=None)

    meta = { 'db_alias': 'default', 'collection': 'law_client' }


    def digest(self):
        return {
            'id': str(self.id),
            'parent': self.parent.digest() if self.parent else None,
            'logo': self.logo,
            'name': self.name,
            'name_cn': self.name_cn,
            'industries': self.industries,
            'status': self.status,
        }

    def detail(self):
        return {
            'id': str(self.id),
            'parent': self.parent.digest() if self.parent else None,
            'logo': self.logo,
            'name': self.name,
            'name_cn': self.name_cn,
            'industries': self.industries,
            'area': self.area,
            'note': self.note,
            'note_cn': self.note_cn,
            'raw': self.raw,
            'status': self.status,
        }


class LawFirm(mongoengine.Document):
    STATUS_CHOICES = (
        (0,'删除'),
        (1,'正常'),
        (2,'注销'),
        (3,'合并'),
    )

    parent = mongoengine.ReferenceField('self',default=None)    # 母公司
    logo = mongoengine.DictField(default=None)

    name = mongoengine.StringField(default='')      # 名称（英文）
    name_cn = mongoengine.StringField(default='')   # 名称（中文）
    website = mongoengine.StringField(default='')   # 网站
    phone = mongoengine.StringField(default='')     # 联系电话
    address = mongoengine.StringField(default='')   # 地址

    categories = mongoengine.ListField(default=[])  # 专业分类
    area = mongoengine.IntField(default=0)          # 所在地区

    note = mongoengine.StringField(default='')      # 描述（英文）
    note_cn = mongoengine.StringField(default='')   # 描述（中文）

    raw = mongoengine.StringField(default='')       # 素材

    opened = mongoengine.IntField()                 # 成立年份
    closed = mongoengine.IntField()                 # 注销年份

    feedbacks = mongoengine.EmbeddedDocumentListField('EmbeddedFeedback',default=[])

    status = mongoengine.IntField(default=1,choices=STATUS_CHOICES)
    created = mongoengine.DateTimeField(default=None)

    meta = { 'db_alias': 'default', 'collection': 'law_firm' }

    def digest(self):
        return {
            'id': str(self.id),
            'parent': self.parent.digest() if self.parent else None,
            'logo': self.logo,
            'name': self.name,
            'name_cn': self.name_cn,
            'categories': self.categories,
            'status': self.status,
        }

    def detail(self):
        return {
            'id': str(self.id),
            'parent': self.parent.digest() if self.parent else None,
            'logo': self.logo,
            'name': self.name,
            'name_cn': self.name_cn,
            'website': self.website,
            'phone': self.phone,
            'address': self.address,
            'categories': self.categories,
            'area': self.area,
            'note': self.note,
            'note_cn': self.note_cn,
            'raw': self.raw,
            'opened': self.opened,
            'closed': self.closed,
            'status': self.status,
        }


class Lawyer(mongoengine.Document):
    GENDER_CHOICES = (
        ('','未知'),
        ('M','男'),
        ('F','女'),
    )

    STATUS_CHOICES = (
        (0,'删除'),
        (1,'正常'),
    )

    avatar = mongoengine.DictField(default=None)

    name = mongoengine.StringField(default='')          # 名字（英文）
    name_cn = mongoengine.StringField(default='')       # 名字（中文）
    gender = mongoengine.StringField(choices=GENDER_CHOICES)

    position = mongoengine.StringField(default='')      # 职称头衔
    categories = mongoengine.ListField(default=[])      # 专业分类

    note = mongoengine.StringField(default='')          # 描述（英文）
    note_cn = mongoengine.StringField(default='')       # 描述（中文）

    raw = mongoengine.StringField(default='')           # 素材

    feedbacks = mongoengine.EmbeddedDocumentListField('EmbeddedFeedback',default=[])

    status = mongoengine.IntField(default=1,choices=STATUS_CHOICES)
    created = mongoengine.DateTimeField(default=None)

    meta = { 'db_alias': 'default', 'collection': 'law_lawyer' }

    def digest(self):
        return {
            'id': str(self.id),
            'avatar': self.avatar,
            'name': self.name,
            'name_cn': self.name_cn,
            'gender': self.gender,
            'position': self.position,
            'categories': self.categories,
        }

    def detail(self):
        return {
            'id': str(self.id),
            'avatar': self.avatar,
            'name': self.name,
            'name_cn': self.name_cn,
            'gender': self.gender,
            'position': self.position,
            'categories': self.categories,
            'note': self.note,
            'note_cn': self.note_cn,
            'raw': self.raw,
        }


class LawDeal(mongoengine.Document):
    ACCESS_CHOICES = (
        (1,'公开'),
        (2,'半公开'),
        (3,'保密'),
    )

    REVIEW_CHOICES = (
        (1,'已确定'),
        (2,'待完善'),
        (3,'有疑问'),
        (4,'仅参考'),
    )

    STATUS_CHOICES = (
        (0,'删除'),
        (1,'已完成'),
        (2,'已公布'),
        (3,'已取消'),
        (4,'未确定'),
    )

    title = mongoengine.StringField(default='')         # 交易标题（英文）
    title_cn = mongoengine.StringField(default='')      # 交易标题（中文）
    date = mongoengine.DateTimeField()                  # 交易时间
    value = mongoengine.IntField(default=0)             # 统计金额（美元）
    value_txt = mongoengine.StringField(default='')     # 交易金额（文本）

    parties = mongoengine.ListField(default=[])         # 交易角色
    categories = mongoengine.ListField(default=[])      # 专业分类
    industries = mongoengine.ListField(default=[])      # 重要客户行业
    areas = mongoengine.ListField(default=[])           # 重要客户地区

    uniqueness = mongoengine.IntField(default=0)        # 特殊指数
    uniqueness_remark = mongoengine.StringField(default='')

    creativity = mongoengine.IntField(default=0)        # 创新指数
    creativity_remark = mongoengine.StringField(default='')

    complexity = mongoengine.IntField(default=0)        # 复杂指数
    complexity_remark = mongoengine.StringField(default='')

    influence = mongoengine.IntField(default=0)         # 影响指数
    influence_remark = mongoengine.StringField(default='')

    deduction = mongoengine.IntField(default=0)         # 扣减指数
    deduction_remark = mongoengine.StringField(default='')

    note = mongoengine.StringField(default='')          # 描述（英文）
    note_cn = mongoengine.StringField(default='')       # 描述（中文）

    raw = mongoengine.StringField(default='')           # 素材

    access = mongoengine.IntField(default=1,choices=ACCESS_CHOICES)
    review = mongoengine.IntField(default=1,choices=REVIEW_CHOICES)
    status = mongoengine.IntField(default=1,choices=STATUS_CHOICES)
    created = mongoengine.DateTimeField(default=None)

    clients = mongoengine.EmbeddedDocumentListField('EmbeddedDealClient',default=[])
    firms = mongoengine.EmbeddedDocumentListField('EmbeddedDealFirm',default=[])
    lawyers = mongoengine.EmbeddedDocumentListField('EmbeddedDealLawyer',default=[])

    ref_clients = mongoengine.ListField(mongoengine.ReferenceField('LawClient'),default=[])
    ref_firms = mongoengine.ListField(mongoengine.ReferenceField('LawFirm'),default=[])
    ref_lawyers = mongoengine.ListField(mongoengine.ReferenceField('Lawyer'),default=[])

    meta = { 'db_alias': 'default', 'collection': 'law_deal' }


    @property
    def score(self):
        return self.uniqueness + self.creativity + self.complexity + self.influence - self.deduction

    def digest(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'title_cn': self.title_cn,
            'date': int(self.date.timestamp()*1000) if self.date else None,
            'value': self.value,
            'value_txt': self.value_txt,
            'access': self.access,
            'review': self.review,
            'status': self.status,
        }

    def detail(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'title_cn': self.title_cn,
            'date': int(self.date.timestamp()*1000) if self.date else None,
            'value': self.value,
            'value_txt': self.value_txt,

            'categories': self.categories,
            'industries': self.industries,
            'areas': self.areas,

            'uniqueness': self.uniqueness,
            'uniqueness_remark': self.uniqueness_remark,
            'creativity': self.creativity,
            'creativity_remark': self.creativity_remark,
            'complexity': self.complexity,
            'complexity_remark': self.complexity_remark,
            'influence': self.influence,
            'influence_remark': self.influence_remark,
            'deduction': self.deduction,
            'deduction_remark': self.deduction_remark,

            'note': self.note,
            'note_cn': self.note_cn,
            'raw': self.raw,

            'access': self.access,
            'review': self.review,
            'status': self.status,
        }


class EmbeddedFeedback(mongoengine.EmbeddedDocument):
    id = mongoengine.ObjectIdField(default=None)
    name = mongoengine.StringField(default='')
    name_cn = mongoengine.StringField(default='')
    content = mongoengine.StringField(default='')
    content_cn = mongoengine.StringField(default='')
    rating = mongoengine.IntField(default=0)
    created = mongoengine.DateTimeField(default=None)

    def detail(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'name_cn': self.name_cn,
            'content': self.content,
            'content_cn': self.content_cn,
            'rating': self.rating,
            'created': int(self.created.timestamp()*1000) if self.created else 0,
        }


class EmbeddedDealClient(mongoengine.EmbeddedDocument):
    client = mongoengine.ReferenceField('LawClient')
    major = mongoengine.IntField(default=0)
    party = mongoengine.IntField(default=None)
    industries = mongoengine.ListField(default=[])
    areas = mongoengine.ListField(default=[])
    remark = mongoengine.StringField(default='')

    def detail(self):
        client = self.client.digest()
        client.update({
            'major': self.major,
            'party': self.party,
            'industries': self.industries,
            'areas': self.areas,
            'remark': self.remark,
        })
        return client


class EmbeddedDealFirm(mongoengine.EmbeddedDocument):
    firm = mongoengine.ReferenceField('LawFirm')
    party = mongoengine.IntField(default=None)
    areas = mongoengine.ListField(default=[])
    remark = mongoengine.StringField(default='')

    def detail(self):
        firm = self.firm.digest()
        firm.update({
            'party': self.party,
            'areas': self.areas,
            'remark': self.remark,
        })
        return firm


class EmbeddedDealLawyer(mongoengine.EmbeddedDocument):
    lawyer = mongoengine.ReferenceField('Lawyer')
    firm = mongoengine.ReferenceField('LawFirm')
    role = mongoengine.IntField(default=0)
    remark = mongoengine.StringField(default='')

    def detail(self):
        lawyer = self.lawyer.digest()
        lawyer.update({
            'firm': self.firm.digest(),
            'role': self.role,
            'remark': self.remark,
        })
        return lawyer


class LawExchangeCurrency(mongoengine.Document):
    code = mongoengine.StringField(default='')          # 货币代码
    name = mongoengine.StringField(default='')          # 名称（英文）
    name_cn = mongoengine.StringField(default='')       # 名称（中文）
    start = mongoengine.DateTimeField(default=None)
    end = mongoengine.DateTimeField(default=None)

    meta = { 'db_alias': 'default', 'collection': 'law_exchange_currency' }


    def detail(self):
        return {
            'code': self.code,
            'name': self.name,
            'name_cn': self.name_cn,
            'start': int(self.start.timestamp()*1000) if self.start else 0,
            'end': int(self.end.timestamp()*1000) if self.end else 0,
        }


class LawExchangeHistory(mongoengine.Document):
    quote = mongoengine.StringField(default='')         # 报价货币
    base = mongoengine.StringField(default='')          # 基本货币
    year = mongoengine.IntField(default=0)              # 历史年份
    logs = mongoengine.DictField(default='')            # 汇率日志

    meta = { 'db_alias': 'default', 'collection': 'law_exchange_history' }


    def detail(self):
        return {
            'code': self.code,
            'year': self.year,
            'logs': self.logs,
        }
