# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result

import json,datetime

from mongoengine import Q

from service.law.utils.stats import compute_firm_ranking
from service.law.models import LawDeal,LawFirm


class StatsHandler(ThriftHandler):
    def __init__(self):
        super(StatsHandler,self).__init__()

    def render_m1(self,request):
        start = int(request.data.get('start',0))
        end = int(request.data.get('end',0))
        categories = [int(category) for category in request.data.get('categories',[])]
        industries = [int(industry) for industry in request.data.get('industries',[])]
        areas = [int(area) for area in request.data.get('areas',[])]

        if not start or not end:
            raise BizException('非法的时间参数')

        start = datetime.datetime.fromtimestamp(start/1000.0)
        end = datetime.datetime.fromtimestamp(end/1000.0)
        if start >= end:
            raise BizException('结束时间必须大于起始时间')

        if end.month == 12:
            end = datetime.datetime.strptime(str(end.year+1),'%Y')
        else:
            end = datetime.datetime.strptime(str(end.year)+str(end.month+1).zfill(2),'%Y%m')

        deals = LawDeal.objects.filter(date__ne=None).filter(date__gte=start,date__lt=end)

        if categories:
            category_query = Q()
            for category in categories:
                category_query = category_query | Q(categories=category)
            deals = deals.filter(category_query)

        if industries:
            industry_query = Q()
            for industry in industries:
                industry_query = industry_query | Q(industries=industry)
            deals = deals.filter(industry_query)

        if areas:
            area_query = Q()
            for area in areas:
                area_query = area_query | Q(areas=area)
            deals = deals.filter(area_query)

        # query optimization
        deals = deals.only('title','title_cn','date','value','value_txt')
        deals = deals.only('access','review','status','firms','lawyers')
        deals = deals.only('uniqueness','uniqueness_remark','creativity','creativity_remark')
        deals = deals.only('complexity','complexity_remark','influence','influence_remark')
        deals = deals.only('deduction','deduction_remark')
        deals = deals.batch_size(100).select_related(2)

        ranking_deals = []
        firm_stats = {}
        lawyer_stats = {}

        for deal in deals:
            ranking_deals.append({
                'id': str(deal.id),
                'title': deal.title,
                'title_cn': deal.title_cn,
                'date': int(deal.date.timestamp()*1000),
                'value': deal.value,
                'value_txt': deal.value_txt,

                'uniqueness': deal.uniqueness,
                'uniqueness_remark': deal.uniqueness_remark,
                'creativity': deal.creativity,
                'creativity_remark': deal.creativity_remark,
                'complexity': deal.complexity,
                'complexity_remark': deal.complexity_remark,
                'influence': deal.influence,
                'influence_remark': deal.influence_remark,
                'deduction': deal.deduction,
                'deduction_remark': deal.deduction_remark,
                'score': deal.score,

                'review': deal.review,
                'status': deal.status,
            })

            record = {
                'id': str(deal.id),
                'title': deal.title,
                'title_cn': deal.title_cn,
                'date': int(deal.date.timestamp()*1000),
                'value': deal.value,
                'value_txt': deal.value_txt,
                'review': deal.review,
                'status': deal.status,
            }

            for embed in deal.firms:
                firm = embed.firm
                firm_id = str(firm.id)
                if not firm_stats.get(firm_id,{}):
                    firm_stats[firm_id] = {
                        'id': firm_id,
                        'name': firm.name,
                        'name_cn': firm.name_cn,
                        'deals': [record],
                        'volume': 0,
                        'score': 0,
                    }

                elif record not in firm_stats[firm_id]['deals']:
                    firm_stats[firm_id]['deals'].append(record)

                if deal.review != 3:
                    firm_stats[firm_id]['volume'] += deal.value
                    firm_stats[firm_id]['score'] += deal.score

            for embed in deal.lawyers:
                lawyer = embed.lawyer
                lawyer_id = str(lawyer.id)
                if not lawyer_stats.get(lawyer_id,{}):
                    lawyer_stats[lawyer_id] = {
                        'id': lawyer_id,
                        'avatar': lawyer.avatar,
                        'name': lawyer.name,
                        'name_cn': lawyer.name_cn,
                        'deals': [record],
                        'volume': 0,
                        'score': 0,
                    }

                elif record not in lawyer_stats[lawyer_id]['deals']:
                    lawyer_stats[lawyer_id]['deals'].append(record)

                if deal.review != 3:
                    lawyer_stats[lawyer_id]['volume'] += deal.value
                    lawyer_stats[lawyer_id]['score'] += deal.score

        ranking_deals.sort(key=lambda x: x['score'], reverse=True)

        ranking_firms = [firm_stats[key] for key in firm_stats]
        ranking_firms.sort(key=lambda x: (x['score'],x['volume']), reverse=True)

        ranking_lawyers = [lawyer_stats[key] for key in lawyer_stats]
        ranking_lawyers.sort(key=lambda x: (x['score'],x['volume']), reverse=True)

        return Result(data=dict(deals=ranking_deals,firms=ranking_firms,lawyers=ranking_lawyers))

    def render_m2(self,request):
        deals = LawDeal.objects.filter(date__ne=None,value__gt=0,review__ne=3)

        firm_ids = []
        for item in request.data['firms']:
            firm_ids.append(item['id'] if isinstance(item,dict) else item)

        firm_query = Q()
        for firm in LawFirm.objects.filter(id__in=firm_ids):
            firm_query = firm_query | Q(ref_firms=firm)

        deals = deals.filter(firm_query)

        start = int(request.data.get('start',0))
        end = int(request.data.get('end',0))
        categories = [int(category) for category in request.data.get('categories',[])]
        industries = [int(industry) for industry in request.data.get('industries',[])]
        areas = [int(area) for area in request.data.get('areas',[])]

        if not start or not end:
            raise BizException('非法的时间参数')

        start = datetime.datetime.fromtimestamp(start/1000.0)
        end = datetime.datetime.fromtimestamp(end/1000.0)
        if start >= end:
            raise BizException('结束时间必须大于起始时间')

        stats = { 'levels': dict([(i,[]) for i in range(1,8)]), 'months': {}, 'categories': {}, 'industries': {}, 'areas': {} }

        if end.month == 12:
            end = datetime.datetime.strptime(str(end.year+1),'%Y')
        else:
            end = datetime.datetime.strptime(str(end.year)+str(end.month+1).zfill(2),'%Y%m')

        year = start.year
        month = start.month
        key = str(year)+str(month).zfill(2)
        while datetime.datetime.strptime(key,'%Y%m') < end:
            stats['months'][key] = []
            if month < 12:
                month += 1
            else:
                month = 1
                year += 1

            key = str(year)+str(month).zfill(2)

        deals = deals.filter(date__gte=start,date__lt=end)

        if categories:
            category_query = Q()
            for category in categories:
                category_query = category_query | Q(categories=category)
            deals = deals.filter(category_query)

        if industries:
            industry_query = Q()
            for industry in industries:
                industry_query = industry_query | Q(industries=industry)
            deals = deals.filter(industry_query)

        if areas:
            area_query = Q()
            for area in areas:
                area_query = area_query | Q(areas=area)
            deals = deals.filter(area_query)

        # query optimization
        deals = deals.only('title','title_cn','date','value','value_txt')
        deals = deals.only('categories','industries','areas','access','review','status')
        deals = deals.batch_size(100)

        for deal in deals:
            record = {
                'id': str(deal.id),
                'title': deal.title,
                'title_cn': deal.title_cn,
                'date': int(deal.date.timestamp()*1000),
                'value': deal.value,
                'value_txt': deal.value_txt,
                'status': deal.status,
            }

            month = deal.date.strftime('%Y%m')
            stats['months'][month].append(record)

            level = 1
            if deal.value >= 100000000000:
                level = 7
            elif deal.value >= 10000000000:
                level = 6
            elif deal.value >= 1000000000:
                level = 5
            elif deal.value >= 100000000:
                level = 4
            elif deal.value >= 10000000:
                level = 3
            elif deal.value >= 1000000:
                level = 2

            stats['levels'][level].append(record)

            for category in deal.categories:
                if not stats['categories'].get(category,[]):
                    stats['categories'][category] = [record]
                elif record not in stats['categories'][category]:
                    stats['categories'][category].append(record)

            for industry in deal.industries:
                if not stats['industries'].get(industry,[]):
                    stats['industries'][industry] = [record]
                elif record not in stats['industries'][industry]:
                    stats['industries'][industry].append(record)

            for area in deal.areas:
                if not stats['areas'].get(area,[]):
                    stats['areas'][area] = [record]
                elif record not in stats['areas'][area]:
                    stats['areas'][area].append(record)

        extract = lambda key: [dict(dimension=dimension,deals=stats[key][dimension]) for dimension in stats[key]]

        return Result(data=dict(
            months=extract('months'),
            levels=extract('levels'),
            categories=extract('categories'),
            industries=extract('industries'),
            areas=extract('areas'),
        ))

    def render_custom(self,request):
        _stats = json.loads(REDIS['app'].get('deal:stats') or '[]')
        if _stats:
            return Result(data=dict(stats=_stats))

        start = datetime.datetime.strptime('20160101','%Y%m%d')
        end = datetime.datetime.strptime('20170101','%Y%m%d')

        stats = {}
        year = start.year
        month = start.month
        key = str(year)+str(month).zfill(2)
        while datetime.datetime.strptime(key,'%Y%m') < end:
            stats[key] = { 'count': 0, 'volume': 0 }
            if month < 12:
                month += 1
            else:
                month = 1
                year += 1

            key = str(year)+str(month).zfill(2)

        deals = LawDeal.objects.filter(date__ne=None)
        deals = deals.filter(date__gte=start,date__lte=end)

        # query optimization
        deals = deals.only('date','value')
        deals = deals.batch_size(100)

        for deal in deals:
            month = deal.date.strftime('%Y%m')
            stats[month]['count'] += 1
            stats[month]['volume'] += (deal.value or 0)

        _stats = [dict(dimension=dimension,count=stats[dimension]['count'],volume=stats[dimension]['volume']) for dimension in stats]

        now = datetime.datetime.now()
        tomorrow = datetime.datetime.strptime(now.strftime('%Y%m%d'),'%Y%m%d') + datetime.timedelta(days=1)
        timeout = int(tomorrow.timestamp() - now.timestamp())
        REDIS['app'].set('deal:stats',json.dumps(_stats),ex=timeout)
        return Result(data=dict(stats=_stats))

    def list_ranking_firms(self,request):
        if not REDIS['app'].exists('firm:rank:whole'):
            compute_firm_ranking()

        prc_firms = json.loads(REDIS['app'].get('firm:rank:prc') or '[]')
        global_firms = json.loads(REDIS['app'].get('firm:rank:global') or '[]')
        return Result(data=dict(prc_firms=prc_firms[:20],global_firms=global_firms[:20]))

    def list_ranking_deals(self,request):
        _deals = json.loads(REDIS['app'].get('deal:recent') or '[]')
        if _deals:
            return Result(data=dict(deals=_deals))

        deals = LawDeal.objects.filter(date__ne=None).order_by('-date')

        # query optimization
        deals = deals.only('title','title_cn','date','value')

        _deals = []
        for deal in deals[:15]:
            _deal = {
                'id': str(deal.id),
                'title': deal.title,
                'title_cn': deal.title_cn,
                'date': int(deal.date.timestamp()*1000),
                'value': deal.value,
                'value_txt': deal.value_txt,
                'status': deal.status,
                'score': deal.score,
            }

            _deals.append(_deal)

        now = datetime.datetime.now()
        tomorrow = datetime.datetime.strptime(now.strftime('%Y%m%d'),'%Y%m%d') + datetime.timedelta(days=1)
        timeout = int(tomorrow.timestamp() - now.timestamp())
        REDIS['app'].set('deal:recent',json.dumps(_deals),ex=timeout)
        return Result(data=dict(deals=_deals))

    def analyse_recent_by_firm(self,request):
        start = datetime.datetime.strptime('20160101','%Y%m%d')
        end = datetime.datetime.strptime('20161231','%Y%m%d')

        stats = {}
        year = start.year
        month = start.month
        key = str(year)+str(month).zfill(2)
        while datetime.datetime.strptime(key,'%Y%m') < end:
            stats[key] = { 'count': 0, 'volume': 0 }
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

            key = str(year)+str(month).zfill(2)

        firm_id = request.data['firm']
        firm = LawFirm.objects.filter(id=firm_id).first()
        if not firm:
            raise BizException('律所不存在')

        deals = LawDeal.objects.filter(status__ne=0).filter(date__gte=start,date__lte=end)
        deals = deals.filter(ref_firms=firm).order_by('-date')

        # query optimization
        deals = deals.only('title','title_cn','date','value','value_txt','status','lawyers')
        deals = deals.batch_size(100).select_related(2)

        _deals = []
        _lawyers = []
        for deal in deals[:5]:
            month = deal.date.strftime('%Y%m')
            stats[month]['count'] += 1
            stats[month]['volume'] += (deal.value or 0)

            _deals.append({
                'id': str(deal.id),
                'title': deal.title,
                'title_cn': deal.title_cn,
                'date': int(deal.date.timestamp()*1000),
                'value': deal.value,
                'value_txt': deal.value_txt,
                'status': deal.status,
            })

            if len(_lawyers) >= 15:
                continue

            for embed in deal.lawyers.filter(firm=firm):
                if len(_lawyers) >= 15:
                   break

                lawyer = embed.lawyer
                _lawyer = {
                    'id': str(lawyer.id),
                    'name': lawyer.name,
                    'name_cn': lawyer.name_cn,
                    'gender': lawyer.gender,
                    'avatar': lawyer.avatar,
                }

                if _lawyer not in _lawyers:
                    _lawyers.append(_lawyer)

        _stats = [dict(
            dimension=dimension,
            count=stats[dimension]['count'],
            volume=stats[dimension]['volume'],
        ) for dimension in stats]

        return Result(data=dict(stats=_stats,deals=_deals,lawyers=_lawyers))

    def analyse_recent_by_lawyer(self,request):
        return Result(data=dict())



