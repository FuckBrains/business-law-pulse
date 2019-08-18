# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os

from mongoengine import Q

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

from service.law.models import LawClient


class ClientHandler(ThriftHandler):

    @property
    @thrift_exempt
    def default_logo(self):
        if hasattr(self,'_default_logo'):
            return self._default_logo

        module,app = self.__class__.__module__.split('.')[:2]
        name = self.__class__.__name__
        gid = '%s.%s.%s' % (module,app,name)
        with thrift_connect(service=common_thrift.ImageService) as image_service:
            payload = Payload(gid=gid,data=dict(scene='law/client/logo',path='images/default/law_client_logo.png'))
            result = image_service.construct(payload)
            self._default_logo = result.data['image']

        return self._default_logo

    def filter(self,request):
        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        clients = LawClient.objects.filter(status__ne=0)

        if keyword:
            clients = clients.filter(Q(name__icontains=keyword) | Q(name_cn__icontains=keyword))

        if page.get('no'):
            total = clients.count()
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            clients = clients.order_by('-created')[start:end]
        else:
            base_id = page.get('base',{}).get('id') or '0'*24
            base = LawClient.objects.filter(id=base_id).first()

            if not base:
                total = clients.count()
                clients = clients.order_by('-created')[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    clients = clients.filter(created__gt=base.created)
                    total = clients.count()
                    clients = clients.order_by('-created')[max(0,clients.count()-page['size']):]
                else:
                    clients = clients.filter(created__lt=base.created)
                    total = clients.count()
                    clients = clients.order_by('-created')[:page['size']]

        _clients = [client.digest() for client in clients]
        return Result(data=dict(clients=_clients,total=total))

    @check_admin_auth(permissions=['create_law_client'])
    def create(self,request):
        logo = request.data.get('logo','')
        name = request.data.get('name','').strip()
        name_cn = request.data.get('name_cn','').strip()
        parent = request.data.get('parent','') or '0'*24
        status = int(request.data.get('status',1))
        industries = [int(industry) for industry in request.data.get('industries',[])]
        area = int(request.data.get('area',0))
        note = request.data.get('note','')
        note_cn = request.data.get('note_cn','')
        raw = request.data.get('raw','')

        if not name and not name_cn:
            raise BizException('客户名称不能为空')

        if logo:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=logo))
                result = image_service.extract(payload)
                logo = result['data']['image']

        client = LawClient()
        client.logo = logo or self.default_logo
        client.parent = LawClient.objects.filter(id=parent).first()
        client.name = name
        client.name_cn = name_cn
        client.status = status
        client.industries = industries
        client.area = area
        client.note = note
        client.note_cn = note_cn
        client.raw = raw
        client.switch_db('primary').save()
        return Result(msg='添加成功',data=dict(client=client.detail()))


    @check_admin_auth(permissions=['update_law_client'])
    def update(self,request):
        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()
        if not client:
            raise BizException('客户记录不存在')

        logo = request.data.get('logo','')
        if logo:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=logo))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    client.logo = image

        name = request.data.get('name',None)
        if name is not None and name.strip():
            client.name = name.strip()

        name_cn = request.data.get('name_cn',None)
        if name_cn is not None and name_cn.strip():
            client.name_cn = name_cn.strip()

        status = request.data.get('status',None)
        if status is not None:
            client.status = int(status)

        parent = request.data.get('parent',None)
        if parent:
            client.parent = LawClient.objects.filter(id=parent).first()

        industries = request.data.get('industries',None)
        if industries is not None:
            client.industries = [int(industry) for industry in industries]

        area = request.data.get('area',None)
        if area is not None:
            client.area = int(area)

        note = request.data.get('note',None)
        if note is not None:
            client.note = note

        note_cn = request.data.get('note_cn',None)
        if note_cn is not None:
            client.note_cn = note_cn

        raw = request.data.get('raw',None)
        if raw is not None:
            client.raw = raw

        client.switch_db('primary').save()
        return Result(msg='修改成功')

    @check_admin_auth(permissions=['remove_law_client'])
    def remove(self,request):
        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()
        if not client:
            raise BizException('客户记录不存在')

        client.status = 0
        client.switch_db('primary').save()
        return Result(msg='删除成功')

    def get_digest(self,request):
        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()

        _client = client.digest() if client else None
        return Result(data=dict(client=_client))

    def get_detail(self,request):
        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()

        _client = client.detail() if client else None
        if client and not request.auth:
            del _client['raw']
            del _client['note']
            del _client['note_cn']

        return Result(data=dict(client=_client))

    def get_multiple(self,request):
        client_ids = []
        for item in request.data['clients']:
            client_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(client_ids) > 100:
            raise BizException('记录数量超过上限')

        clients = LawClient.objects.filter(id__in=client_ids)

        _clients = [client.digest() for client in clients]
        return Result(data=dict(clients=_clients))



