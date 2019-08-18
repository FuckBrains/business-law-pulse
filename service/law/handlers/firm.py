# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os,datetime,re
from bson import ObjectId
from mongoengine import Q

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

from service.law.models import LawFirm,EmbeddedFeedback


class FirmHandler(ThriftHandler):

    @property
    @thrift_exempt
    def default_logo(self):
        if hasattr(self,'_default_logo'):
            return self._default_logo

        module,app = self.__class__.__module__.split('.')[:2]
        name = self.__class__.__name__
        gid = '%s.%s.%s' % (module,app,name)
        with thrift_connect(service=common_thrift.ImageService) as image_service:
            payload = Payload(gid=gid,data=dict(scene='law/firm/logo',path='images/default/law_firm_logo.png'))
            result = image_service.construct(payload)
            self._default_logo = result.data['image']

        return self._default_logo

    def filter(self,request):
        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        firms = LawFirm.objects.filter(status__ne=0)

        if keyword:
            firms = firms.filter(Q(name__icontains=keyword) | Q(name_cn__icontains=keyword))

        if page.get('no'):
            total = firms.count()
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            firms = firms.order_by('-created')[start:end]
        else:
            base_id = page.get('base',{}).get('id') or '0'*24
            base = LawFirm.objects.filter(id=base_id).first()

            if not base:
                total = deals.count()
                firms = firms.order_by('-created')[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    firms = firms.filter(created__gt=base.created)
                    total = firms.count()
                    firms = firms.order_by('-created')[max(0,total-page['size']):]
                else:
                    firms = firms.filter(created__lt=base.created)
                    total = firms.count()
                    firms = firms.order_by('-created')[:page['size']]

        _firms = [firm.digest() for firm in firms]
        return Result(data=dict(firms=_firms,total=total))

    @check_admin_auth(permissions=['create_law_firm'])
    def create(self,request):
        logo = request.data.get('logo','')
        name = request.data.get('name','').strip()
        name_cn = request.data.get('name_cn','').strip()
        website = request.data.get('website','').strip()
        phone = request.data.get('phone','').strip()
        address = request.data.get('address','').strip()
        parent = request.data.get('parent','') or '0'*24
        opened = int(request.data.get('opened',0))
        closed = int(request.data.get('closed',0))
        status = int(request.data.get('status',1))
        categories = [int(category) for category in request.data.get('categories',[])]
        area = int(request.data.get('area',0))
        note = request.data.get('note','')
        note_cn = request.data.get('note_cn','')
        raw = request.data.get('raw','')

        if not name and not name_cn:
            raise BizException('律所名称不能为空')

        if logo:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=logo))
                result = image_service.extract(payload)
                logo = result['data']['image']

        firm = LawFirm()
        firm.logo = logo or self.default_logo
        firm.parent = LawFirm.objects.filter(id=parent).first()
        firm.name = name
        firm.name_cn = name_cn
        firm.website = website
        firm.phone = phone
        firm.address = address
        firm.opened = opened
        firm.closed = closed
        firm.status = status
        firm.categories = categories
        firm.area = area
        firm.note = note
        firm.note_cn = note_cn
        firm.raw = raw
        firm.switch_db('primary').save()
        return Result(msg='添加成功',data=dict(firm=firm.detail()))


    @check_admin_auth(permissions=['update_law_firm'])
    def update(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        logo = request.data.get('logo','')
        if logo:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=logo))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    firm.logo = image

        name = request.data.get('name',None)
        if name is not None and name.strip():
            firm.name = name.strip()

        name_cn = request.data.get('name_cn',None)
        if name_cn is not None and name_cn.strip():
            firm.name_cn = name_cn.strip()

        website = request.data.get('website',None)
        if website is not None:
            firm.website = website.strip()

        phone = request.data.get('phone',None)
        if phone is not None:
            firm.phone = phone.strip()

        address = request.data.get('address',None)
        if address is not None:
            firm.address = address.strip()

        opened = request.data.get('opened',None)
        if opened is not None:
            firm.opened = int(opened)

        closed = request.data.get('closed',None)
        if closed is not None:
            firm.closed = int(closed)

        status = request.data.get('status',None)
        if status is not None:
            firm.status = int(status)

        parent = request.data.get('parent',None)
        if parent:
            firm.parent = LawFirm.objects.filter(id=parent).first()

        categories = request.data.get('categories',None)
        if categories is not None:
            categories = [int(category) for category in categories]
            firm.categories = categories

        area = request.data.get('area',None)
        if area is not None:
            firm.area = int(area)

        note = request.data.get('note',None)
        if note is not None:
            firm.note = note

        note_cn = request.data.get('note_cn',None)
        if note_cn is not None:
            firm.note_cn = note_cn

        raw = request.data.get('raw',None)
        if raw is not None:
            firm.raw = raw

        firm.switch_db('primary').save()
        return Result(msg='修改成功')

    @check_admin_auth(permissions=['remove_law_firm'])
    def remove(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        firm.status = 0
        firm.switch_db('primary').save()
        return Result(msg='删除成功')

    def get_digest(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()

        _firm = firm.digest() if firm else None
        return Result(data=dict(firm=_firm))

    def get_detail(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        _firm = firm.detail() if firm else None
        if firm and not request.auth:
            del _firm['raw']
            del _firm['note']
            del _firm['note_cn']

        return Result(data=dict(firm=_firm))

    def get_multiple(self,request):
        firm_ids = []
        for item in request.data['firms']:
            firm_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(firm_ids) > 100:
            raise BizException('记录数量超过上限')

        firms = LawFirm.objects.filter(id__in=firm_ids)

        _firms = [firm.digest() for firm in firms]
        return Result(data=dict(firms=_firms))

    def list_children(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        firms = LawFirm.objects.filter(parent=firm)

        _firms = [firm.digest() for firm in firms]
        return Result(data=dict(firms=_firms))

    def filter_feedbacks(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        feedbacks = firm.feedbacks
        if keyword:
            pattern = keyword.replace('$','\$')
            query = lambda x: re.search(pattern,x.name) or re.search(pattern,x.content) or \
                                re.search(pattern,x.name_cn) or re.search(pattern,x.content_cn)
            feedbacks = [item for item in filter(query,feedbacks)]

        if page.get('no'):
            total = len(feedbacks)
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            feedbacks = feedbacks[start:end]
        else:
            base_id = page.get('base',{}).get('id') or '0'*24
            query = lambda x: str(x.id) == base_id
            base = [item for item in filter(query, feedbacks)]
            base = base.index(0) if base else None

            if not base:
                total = len(feedbacks)
                feedbacks = feedbacks[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    query = lambda x: x.created > base.created
                    feedbacks = [item for item in filter(query,feedbacks)]
                    total = len(feedbacks)
                    feedbacks = feedbacks[max(0,len(feedbacks)-page['size']):]
                else:
                    query = lambda x: x.created < base.created
                    feedbacks = [item for item in filter(query,feedbacks)]
                    total = len(feedbacks)
                    feedbacks = feedbacks[:page['size']]

        _feedbacks = [feedback.detail() for feedback in feedbacks]
        return Result(data=dict(feedbacks=_feedbacks,total=total))

    @check_admin_auth(permissions=['create_firm_feedback'])
    def create_feedback(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        name = request.data['name'].strip()
        content = request.data['content'].strip()
        name_cn = request.data['name_cn'].strip()
        content_cn = request.data['content_cn'].strip()
        created = int(request.data['created'] or 0)
        rating = int(request.data['rating'] or 0)

        if not name and not content and not name_cn and not content_cn:
            raise BizException('不能提交空反馈')

        if created:
            created = datetime.datetime.fromtimestamp(created/1000)
        else:
            created = datetime.datetime.now()

        feedback = EmbeddedFeedback(
            id=ObjectId(),
            name=name, content=content,
            name_cn=name_cn, content_cn=content_cn,
            created=created+datetime.timedelta(microseconds=datetime.datetime.now().microsecond),
            rating=rating,
        )

        firm.feedbacks.append(feedback)
        firm.feedbacks.sort(key=lambda x:-x.created.timestamp())
        firm.switch_db('primary').save()
        return Result(msg='添加成功')

    @check_admin_auth(permissions=['remove_firm_feedback'])
    def remove_feedback(self,request):
        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        feedback_id = request.data['feedback'] or '0'*24
        feedback = firm.feedbacks.filter(id=ObjectId(feedback_id)).first()
        if not feedback:
            raise BizException('反馈记录不存在')

        firm.feedbacks.remove(feedback)
        firm.switch_db('primary').save()
        return Result(msg='添加成功')


