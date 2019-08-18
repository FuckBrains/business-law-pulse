# -*- coding: utf-8 -*-


import mongoengine



class SystemConfig(mongoengine.Document):
    key = mongoengine.StringField(default='')
    value = mongoengine.DynamicField(default={})

    meta = { 'db_alias': 'default', 'collection': 'system_config' }

    def detail(self):
        return {
            'key': self.key,
            'value': self.value,
        }


class Feedback(mongoengine.Document):
    content = mongoengine.StringField(default='')
    contact = mongoengine.StringField(default='')
    remark = mongoengine.StringField(default='')
    status = mongoengine.IntField(default=1)
    created = mongoengine.DateTimeField()

    meta = { 'db_alias': 'default', 'collection': 'feedback' }

    def detail(self):
        return {
            'id': str(self.id),
            'content': self.content,
            'contact': self.contact,
            'remark': self.remark,
            'status': self.status,
            'created': int(self.created.timestamp()*1000),
        }


class EmbeddedDocItem(mongoengine.EmbeddedDocument):
    TYPE_CHOICES = (
        (1,'JSON POST'),
        (2,'FORM POST'),
        (3,'GET'),
    )

    id = mongoengine.StringField(default='')
    url = mongoengine.StringField(default='')
    type = mongoengine.IntField(choices=TYPE_CHOICES)
    remark = mongoengine.StringField(default='')
    input = mongoengine.StringField(default='')
    output = mongoengine.StringField(default='')

    def digest(self):
        return {
            'id': self.id,
            'url': self.url,
            'type': self.type,
            'remark': self.remark,
        }

    def detail(self):
        return {
            'id': self.id,
            'url': self.url,
            'type': self.type,
            'remark': self.remark,
            'input': self.input,
            'output': self.output,
        }


class DocModule(mongoengine.Document):
    code = mongoengine.StringField(default='')
    name = mongoengine.StringField(default='')
    remark = mongoengine.StringField(default='')
    items = mongoengine.EmbeddedDocumentListField('EmbeddedDocItem',default=[])

    meta = { 'db_alias': 'default', 'collection': 'doc_module' }

    def digest(self):
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.name,
            'remark': self.remark,
        }



