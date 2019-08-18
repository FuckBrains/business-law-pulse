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

from service.law.models import Lawyer,EmbeddedFeedback
from service.law.models import LawDeal,LawFirm


class LawyerHandler(ThriftHandler):

    @property
    @thrift_exempt
    def default_avatar(self):
        if hasattr(self,'_default_avatar'):
            return self._default_avatar

        module,app = self.__class__.__module__.split('.')[:2]
        name = self.__class__.__name__
        gid = '%s.%s.%s' % (module,app,name)
        with thrift_connect(service=common_thrift.ImageService) as image_service:
            payload = Payload(gid=gid,data=dict(scene='law/lawyer/avatar',path='images/default/law_lawyer_avatar.png'))
            result = image_service.construct(payload)
            self._default_avatar = result.data['image']

        return self._default_avatar

    def filter(self,request):
        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        lawyers = Lawyer.objects.filter(status__ne=0)

        if keyword:
            lawyers = lawyers.filter(Q(name__icontains=keyword) | Q(name_cn__icontains=keyword))

        if page.get('no'):
            total = lawyers.count()
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            lawyers = lawyers.order_by('-created')[start:end]
        else:
            base_id = page.get('base',{}).get('id') or '0'*24
            base = Lawyer.objects.filter(id=base_id).first()

            if not base:
                total = lawyers.count()
                lawyers = lawyers.order_by('-created')[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    lawyers = lawyers.filter(created__gt=base.created)
                    total = lawyers.count()
                    lawyers = lawyers.order_by('-created')[max(0,lawyers.count()-page['size']):]
                else:
                    lawyers = lawyers.filter(created__lt=base.created)
                    total = lawyers.count()
                    lawyers = lawyers.order_by('-created')[:page['size']]

        _lawyers = [lawyer.digest() for lawyer in lawyers]
        return Result(data=dict(lawyers=_lawyers,total=total))

    @check_admin_auth(permissions=['create_lawyer'])
    def create(self,request):
        avatar = request.data.get('avatar','')
        name = request.data.get('name','').strip()
        name_cn = request.data.get('name_cn','').strip()
        position = request.data.get('position','').strip()
        gender = request.data.get('gender','')
        categories = [int(category) for category in request.data.get('categories',[])]
        note = request.data.get('note','')
        note_cn = request.data.get('note_cn','')
        raw = request.data.get('raw','')

        if not name and not name_cn:
            raise BizException('律师名称不能为空')

        if avatar:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=avatar))
                result = image_service.extract(payload)
                avatar = result['data']['image']

        lawyer = Lawyer()
        lawyer.avatar = avatar or self.default_avatar
        lawyer.name = name
        lawyer.name_cn = name_cn
        lawyer.position = position
        lawyer.gender = gender
        lawyer.categories = categories
        lawyer.note = note
        lawyer.note_cn = note_cn
        lawyer.raw = raw
        lawyer.switch_db('primary').save()
        return Result(msg='添加成功',data=dict(lawyer=lawyer.detail()))


    @check_admin_auth(permissions=['update_lawyer'])
    def update(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        avatar = request.data.get('avatar','')
        if avatar:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=avatar))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    lawyer.avatar = image

        name = request.data.get('name',None)
        if name is not None and name.strip():
            lawyer.name = name.strip()

        name_cn = request.data.get('name_cn',None)
        if name_cn is not None and name_cn.strip():
            lawyer.name_cn = name_cn.strip()

        position = request.data.get('position',None)
        if position is not None and position.strip():
            lawyer.position = position.strip()

        gender = request.data.get('gender',None)
        if gender is not None and gender:
            lawyer.gender = gender

        categories = request.data.get('categories',None)
        if categories is not None:
            categories = [int(category) for category in categories]
            lawyer.categories = categories

        note = request.data.get('note',None)
        if note is not None:
            lawyer.note = note

        note_cn = request.data.get('note_cn',None)
        if note_cn is not None:
            lawyer.note_cn = note_cn

        raw = request.data.get('raw',None)
        if raw is not None:
            lawyer.raw = raw

        lawyer.switch_db('primary').save()
        return Result(msg='修改成功')

    @check_admin_auth(permissions=['remove_lawyer'])
    def remove(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        lawyer.status = 0
        lawyer.switch_db('primary').save()
        return Result(msg='删除成功')

    def get_digest(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()

        _lawyer = lawyer.digest() if lawyer else None
        return Result(data=dict(lawyer=_lawyer))

    def get_detail(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        _lawyer = lawyer.detail() if lawyer else None
        if lawyer and not request.auth:
            del _lawyer['raw']
            del _lawyer['note']
            del _lawyer['note_cn']

        return Result(data=dict(lawyer=_lawyer))

    def get_multiple(self,request):
        lawyer_ids = []
        for item in request.data['lawyers']:
            lawyer_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(lawyer_ids) > 100:
            raise BizException('记录数量超过上限')

        lawyers = Lawyer.objects.filter(id__in=lawyer_ids)

        _lawyers = [lawyer.digest() for lawyer in lawyers]
        return Result(data=dict(lawyers=_lawyers))

    def get_career(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        career = {}
        deals = LawDeal.objects.filter(ref_lawyers=lawyer)
        for deal in deals:
            date = int(deal.date.timestamp()*1000) if deal.date else 0
            embed = deal.lawyers.filter(lawyer=lawyer).first()
            if not embed:
                continue

            firm = embed.firm
            firm_id = str(firm.id)
            if firm_id not in career:
                career[firm_id] = {
                    'firm': firm.digest(),
                    'start': date,
                    'end': date,
                    'deals': [deal.digest()],
                }
            else:
                if date and date < career[firm_id]['start']:
                    career[firm_id]['start'] = date

                if date and date > career[firm_id]['end']:
                    career[firm_id]['end'] = date

                career[firm_id]['deals'].append(deal.digest())

        _career = list(career.values())
        _career.sort(key=lambda x: (-x['start'],-x['end']))
        return Result(data=dict(career=_career))

    def filter_feedbacks(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        feedbacks = lawyer.feedbacks
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

    @check_admin_auth(permissions=['create_lawyer_feedback'])
    def create_feedback(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

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

        lawyer.feedbacks.append(feedback)
        lawyer.feedbacks.sort(key=lambda x:-x.created.timestamp())
        lawyer.switch_db('primary').save()
        return Result(msg='添加成功')

    @check_admin_auth(permissions=['remove_lawyer_feedback'])
    def remove_feedback(self,request):
        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = LawFirm.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律所记录不存在')

        feedback_id = request.data['feedback'] or '0'*24
        feedback = lawyer.feedbacks.filter(id=ObjectId(feedback_id)).first()
        if not feedback:
            raise BizException('反馈记录不存在')

        lawyer.feedbacks.remove(feedback)
        lawyer.switch_db('primary').save()
        return Result(msg='添加成功')


