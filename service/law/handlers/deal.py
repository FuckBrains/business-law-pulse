# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result
from core.utils.decorators import check_admin_auth

import datetime
from mongoengine import Q

from service.law.utils.stats import auto_maintain
from service.law.models import LawDeal,LawClient,LawFirm,Lawyer
from service.law.models import EmbeddedDealClient,EmbeddedDealFirm,EmbeddedDealLawyer


class DealHandler(ThriftHandler):
    def __init__(self):
        super(DealHandler,self).__init__()

    def filter(self,request):
        client = request.data.get('client',None)
        firm = request.data.get('firm',None)
        lawyer = request.data.get('lawyer',None)
        keyword = request.data.get('keyword','').strip()
        start = int(request.data.get('start',0))
        end = int(request.data.get('end',0))
        categories = [int(category) for category in request.data.get('category',[])]
        industries = [int(industry) for industry in request.data.get('industry',[])]
        areas = [int(area) for area in request.data.get('areas',[])]
        page = request.data.get('page') or { 'size': 20 }

        deals = LawDeal.objects.filter(status__ne=0)

        if client is not None:
            client = LawClient.objects.filter(id=client or '0'*24).first()
            if client:
                deals = deals.filter(ref_clients=client)

        if firm is not None:
            firm = LawFirm.objects.filter(id=firm or '0'*24).first()
            if firm:
                deals = deals.filter(ref_firms=firm)

        if lawyer is not None:
            lawyer = Lawyer.objects.filter(id=lawyer or '0'*24).first()
            if lawyer:
                deals = deals.filter(ref_lawyers=lawyer)

        if keyword:
            deals = deals.filter(Q(title__icontains=keyword) | Q(title_cn__icontains=keyword))

        if start and end:
            start = datetime.datetime.fromtimestamp(start/1000.0)
            end = datetime.datetime.fromtimestamp(end/1000.0)
            if start >= end:
                raise BizException('结束时间必须大于起始时间')

            if end.month == 12:
                end = datetime.datetime.strptime(str(end.year+1),'%Y')
            else:
                end = datetime.datetime.strptime(str(end.year)+str(end.month+1).zfill(2),'%Y%m')

            deals = deals.filter(happen__gte=start,happen__lt=end)

        if categories:
            categories = [int(category) for category in categories]
            category_query = Q()
            for category in categories:
                category_query = category_query | Q(categories=category)

            deals = deals.filter(category_query)

        if industries:
            industries = [int(industry) for industry in industries]
            industry_query = Q()
            for industry in industries:
                industry_query = industry_query | Q(industries=industry)

            deals = deals.filter(industry_query)

        if areas:
            areas = [int(area) for area in areas]
            area_query = Q()
            for area in areas:
                area_query = area_query | Q(areas=area)

            deals = deals.filter(area_query)

        if page.get('no'):
            total = deals.count()
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            deals = deals.order_by('-date')[start:end]
        else:
            base_id = page.get('base',{}).get('id') or '0'*24
            base = LawDeal.objects.filter(id=base_id).first()

            if not base:
                total = deals.count()
                deals = deals.order_by('-date')[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    deals = deals.filter(created__gt=base.date)
                    total = deals.count()
                    deals = deals.order_by('-date')[max(0,deals.count()-page['size']):]
                else:
                    deals = deals.filter(created__lt=base.date)
                    total = deals.count()
                    deals = deals.order_by('-date')[:page['size']]

        _deals = [deal.digest() for deal in deals]
        return Result(data=dict(deals=_deals,total=total))

    @check_admin_auth(permissions=['create_law_deal'])
    def create(self,request):
        title = request.data.get('title','').strip()
        title_cn = request.data.get('title_cn','').strip()
        categories = [int(category) for category in request.data.get('categroeis',[])]
        value = int(request.data.get('value',0))
        value_txt = request.data.get('value_txt','')
        date = int(request.data.get('date',0))
        status = int(request.data.get('status',1))
        access = int(request.data.get('access',0))
        review = int(request.data.get('review',0))

        uniqueness = int(request.data.get('uniqueness',0))
        uniqueness_remark = request.data.get('uniqueness_remark','').strip()
        creativity = int(request.data.get('creativity',0))
        creativity_remark = request.data.get('creativity_remark','').strip()
        complexity = int(request.data.get('complexity',0))
        complexity_remark = request.data.get('complexity_remark','').strip()
        influence = int(request.data.get('influence',0))
        influence_remark = request.data.get('influence_remark','').strip()
        deduction = int(request.data.get('deduction',5))
        deduction_remark = request.data.get('deduction_remark','').strip()

        note = request.data.get('note','')
        note_cn = request.data.get('note_cn','')
        raw = request.data.get('raw','')

        if not title and not title_cn:
            raise BizException('交易标题不能为空')

        deal = LawDeal()
        deal.title = title
        deal.title_cn = title_cn
        deal.categories = categories
        deal.value = value
        deal.value_txt = value_txt
        deal.date = datetime.datetime.fromtimestamp(date/1000.0) if date else None
        deal.status = status
        deal.access = access
        deal.review = review

        deal.uniqueness = uniqueness
        deal.uniqueness_remark = uniqueness_remark
        deal.creativity = creativity
        deal.creativity_remark = creativity_remark
        deal.complexity = complexity
        deal.complexity_remark = complexity_remark
        deal.influence = influence
        deal.influence_remark = influence_remark
        deal.deduction = deduction
        deal.deduction_remark = deduction_remark

        deal.note = note
        deal.note_cn = note_cn
        deal.raw = raw
        deal.switch_db('primary').save()
        return Result(msg='添加成功',data=dict(deal=deal.detail()))

    @check_admin_auth(permissions=['update_law_deal'])
    def update(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        title = request.data.get('title',None)
        if title is not None and title.strip():
            deal.title = title.strip()

        title_cn = request.data.get('title_cn',None)
        if title_cn is not None and title_cn.strip():
            deal.title_cn = title_cn.strip()

        categories = request.data.get('categories',None)
        if categories is not None:
            categories = [int(category) for category in categories]
            deal.categories = categories

        value = request.data.get('value',None)
        if value is not None:
            deal.value = int(value)

        value_txt = request.data.get('value_txt',None)
        if value_txt is not None:
            deal.value_txt = value_txt.strip()

        date = request.data.get('date',None)
        if date is not None:
            date = int(date)
            deal.date = datetime.datetime.fromtimestamp(date/1000.0) if date else None

        access = request.data.get('access',None)
        if access is not None:
            deal.access = int(access)

        review = request.data.get('review',None)
        if review is not None:
            deal.review = int(review)

        uniqueness = request.data.get('uniqueness',None)
        uniqueness_remark = request.data.get('uniqueness_remark',None)
        if uniqueness and uniqueness_remark and uniqueness_remark.strip():
            deal.uniqueness = int(uniqueness)
            deal.uniqueness_remark = uniqueness_remark.strip()

        creativity = request.data.get('creativity',None)
        creativity_remark = request.data.get('creativity_remark',None)
        if creativity and creativity_remark and creativity_remark.strip():
            deal.creativity = int(creativity)
            deal.creativity_remark = creativity_remark.strip()

        complexity = request.data.get('complexity',None)
        complexity_remark = request.data.get('complexity_remark',None)
        if complexity and complexity_remark and complexity_remark.strip():
            deal.complexity = int(complexity)
            deal.complexity_remark = complexity_remark.strip()

        influence = request.data.get('influence',None)
        influence_remark = request.data.get('influence_remark',None)
        if influence and influence_remark and influence_remark.strip():
            deal.influence = int(influence)
            deal.influence_remark = influence_remark.strip()

        deduction = request.data.get('deduction',None)
        deduction_remark = request.data.get('deduction_remark',None)
        if deduction and deduction_remark and deduction_remark.strip():
            deal.deduction = int(deduction)
            deal.deduction_remark = deduction_remark.strip()

        note = request.data.get('note',None)
        if note is not None:
            deal.note = note

        note_cn = request.data.get('note_cn',None)
        if note_cn is not None:
            deal.note_cn = note_cn

        raw = request.data.get('raw',None)
        if raw is not None:
            deal.raw = raw

        deal.switch_db('primary').save()
        return Result(msg='修改成功')

    @check_admin_auth(permissions=['remove_law_deal'])
    def remove(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        deal.status = 0
        deal.switch_db('primary').save()
        return Result(msg='删除成功')

    def get_digest(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()

        _deal = deal.digest() if deal else None
        return Result(data=dict(deal=_deal))

    def get_detail(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        _deal = deal.detail() if deal else None
        if deal and not request.auth:
            del _deal['raw']
            del _deal['uniqueness']
            del _deal['creativity']
            del _deal['complexity']
            del _deal['influence']
            del _deal['deduction']

        return Result(data=dict(deal=_deal))

    def get_multiple(self,request):
        deal_ids = []
        for item in request.data['deals']:
            deal_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(deal_ids) > 100:
            raise BizException('记录数量超过上限')

        deals = LawDeal.objects.filter(id__in=deal_ids)

        _deals = [deal.digest() for deal in deals]
        return Result(data=dict(deals=_deals))

    def get_relation(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        clients = [embed.detail() for embed in deal.clients]
        clients.sort(key=lambda x: x['party'] or 999)

        firms = [embed.detail() for embed in deal.firms]
        firms.sort(key=lambda x: x['party'] or 999)

        lawyers = [embed.detail() for embed in deal.lawyers]
        lawyers.sort(key=lambda x: x['role'] or 999)

        return Result(data=dict(clients=clients,firms=firms,lawyers=lawyers))

    def list_clients(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        clients = [embed.detail() for embed in deal.clients]
        clients.sort(key=lambda x: x['party'] or 999)

        return Result(data=dict(clients=clients))

    @check_admin_auth
    def add_client(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()
        if not client:
            raise BizException('客户记录不存在')

        if deal.clients.filter(client=client).first():
            raise BizException('交易客户已存在')

        party = int(request.data.get('party',0))
        major = int(request.data.get('major',0))
        industries = [int(industry) for industry in request.data.get('industries',[])]
        areas = [int(area) for area in request.data.get('areas',[])]
        remark = request.data.get('remark','').strip()

        embed = EmbeddedDealClient(client=client)
        embed.party = party
        embed.major = major
        embed.industries = industries
        embed.areas = areas
        embed.remark = remark
        deal.clients.append(embed)
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='添加成功')

    @check_admin_auth
    def update_client(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()
        if not client:
            raise BizException('客户记录不存在')

        embed = deal.clients.filter(client=client).first()
        if not embed:
            raise BizException('交易客户不存在')

        party = int(request.data.get('party',0))
        major = int(request.data.get('major',0))
        industries = [int(industry) for industry in request.data.get('industries',[])]
        areas = [int(area) for area in request.data.get('areas',[])]
        remark = request.data.get('remark','').strip()

        embed.party = party
        embed.major = major
        embed.industries = industries
        embed.areas = areas
        embed.remark = remark
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='修改成功')

    @check_admin_auth
    def remove_client(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        client_id = request.data['client']['id'] if isinstance(request.data['client'],dict) else request.data['client']
        client = LawClient.objects.filter(id=client_id or '0'*24).first()
        if not client:
            raise BizException('客户记录不存在')

        embed = deal.clients.filter(client=client).first()
        if not embed:
            raise BizException('交易客户不存在')

        deal.clients.remove(embed)
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='删除成功')

    def list_firms(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        firms = [embed.detail() for embed in deal.firms]
        firms.sort(key=lambda x: x['party'] or 999)

        return Result(data=dict(firms=firms))

    @check_admin_auth
    def add_firm(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        if deal.firms.filter(firm=firm).first():
            raise BizException('交易律所已存在')

        party = int(request.data.get('party',0))
        areas = [int(area) for area in request.data.get('areas',[])]
        remark = request.data.get('remark','').strip()

        embed = EmbeddedDealFirm(firm=firm)
        embed.party = party
        embed.areas = areas
        embed.remark = remark
        deal.firms.append(embed)
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='添加成功')

    @check_admin_auth
    def update_firm(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        embed = deal.firms.filter(firm=firm).first()
        if not embed:
            raise BizException('交易律所不存在')

        party = int(request.data.get('party',0))
        areas = [int(area) for area in request.data.get('areas',[])]
        remark = request.data.get('remark','').strip()

        embed.party = party
        embed.areas = areas
        embed.remark = remark
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='修改成功')

    @check_admin_auth
    def remove_firm(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        embed = deal.firms.filter(firm=firm).first()
        if not embed:
            raise BizException('交易律所不存在')

        deal.firms.remove(embed)
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='删除成功')

    def list_lawyers(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        lawyers = [embed.detail() for embed in deal.lawyers]
        lawyers.sort(key=lambda x: x['role'] or 999)

        return Result(data=dict(lawyers=lawyers))

    @check_admin_auth
    def add_lawyer(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        if deal.lawyers.filter(lawyer=lawyer).first():
            raise BizException('交易律师已存在')

        role = int(request.data.get('role',0))
        remark = request.data.get('remark','').strip()

        embed = EmbeddedDealLawyer(lawyer=lawyer)
        embed.firm = firm
        embed.role = role
        embed.remark = remark
        deal.lawyers.append(embed)
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='添加成功')

    @check_admin_auth
    def update_lawyer(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        firm_id = request.data['firm']['id'] if isinstance(request.data['firm'],dict) else request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id or '0'*24).first()
        if not firm:
            raise BizException('律所记录不存在')

        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        embed = deal.lawyers.filter(lawyer=lawyer).first()
        if not embed:
            raise BizException('交易律师不存在')

        role = int(request.data.get('role',0))
        remark = request.data.get('remark','').strip()

        embed.firm = firm
        embed.role = role
        embed.remark = remark
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='修改成功')

    @check_admin_auth
    def remove_lawyer(self,request):
        deal_id = request.data['deal']['id'] if isinstance(request.data['deal'],dict) else request.data['deal']
        deal = LawDeal.objects.filter(id=deal_id or '0'*24).first()
        if not deal:
            raise BizException('交易记录不存在')

        lawyer_id = request.data['lawyer']['id'] if isinstance(request.data['lawyer'],dict) else request.data['lawyer']
        lawyer = Lawyer.objects.filter(id=lawyer_id or '0'*24).first()
        if not lawyer:
            raise BizException('律师记录不存在')

        embed = deal.lawyers.filter(lawyer=lawyer).first()
        if not embed:
            raise BizException('交易律师不存在')

        deal.lawyers.remove(embed)
        deal.switch_db('primary').save()

        auto_maintain(deal)
        return Result(msg='删除成功')



