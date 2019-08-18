# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.exceptions import BizException

import json,datetime
import numpy
from scipy.stats import norm

from service.law.models import LawDeal



def auto_maintain(deal):
    parties = []
    industries = []
    areas = []

    deal.ref_clients = []
    for embed in deal.clients:
        deal.ref_clients.append(embed.client)
        parties.append(embed.party)
        industries += embed.industries
        areas += embed.areas

    deal.ref_firms = []
    for embed in deal.firms:
        deal.ref_firms.append(embed.firm)
        parties.append(embed.party)
        areas += embed.areas

    deal.ref_lawyers = []
    for embed in deal.lawyers:
        deal.ref_lawyers.append(embed.lawyer)

    deal.parties = list(set(parties))
    deal.industries = list(set(industries))
    deal.areas = list(set(areas))
    deal.switch_db('primary').save()



def compute_firm_ranking():
    start = datetime.datetime.strptime('20160101','%Y%m%d')
    end = datetime.datetime.strptime('20161231','%Y%m%d')
    if start > end:
        raise BizException('开始时间不得大于结束时间')

    deals = LawDeal.objects.filter(status__ne=0).filter(date__gte=start,date__lte=end)

    # query optimization
    deals = deals.only('status','date','value','uniqueness','creativity','complexity','influence','deduction','firms')
    deals = deals.batch_size(500).select_related(2)

    info = {}
    for deal in deals:
        for embed in deal.firms:
            firm_id = str(embed.firm.id)
            if firm_id in info:
                info[firm_id]['number'] += 1
                info[firm_id]['volume'] += deal.value
                info[firm_id]['score'] += deal.score
            else:
                firm = embed.firm
                info[firm_id] = {
                    'id': firm_id,
                    'logo': firm.logo,
                    'name': firm.name,
                    'name_cn': firm.name_cn,
                    'area': firm.area,
                    'number': 1,
                    'volume': deal.value,
                    'score': deal.score,
                }

    firms = list(info.values())

    number_array = numpy.array([firm['number'] for firm in firms])
    number_norm = lambda x: round(norm.cdf(x,number_array.mean(),number_array.std())*10000)/100

    volume_array = numpy.array([firm['volume'] for firm in firms])
    volume_norm = lambda x: round(norm.cdf(x,volume_array.mean(),volume_array.std())*10000)/100

    avg_volume_array = numpy.array([round(firm['volume']/firm['number']) for firm in firms])
    avg_volume_norm = lambda x: round(norm.cdf(x,avg_volume_array.mean(),avg_volume_array.std())*10000)/100

    score_array = numpy.array([firm['score'] for firm in firms])
    score_norm = lambda x: round(norm.cdf(x,score_array.mean(),score_array.std())*10000)/100

    avg_score_array = numpy.array([round(firm['score']*100/firm['number'])/100 for firm in firms])
    avg_score_norm = lambda x: round(norm.cdf(x,avg_score_array.mean(),avg_score_array.std())*10000)/100

    formula = json.loads(REDIS['app'].get('law:config:formula') or 'null')
    if not formula:
        formula = {
            'std_volume': 30,
            'std_avg_volume': 10,
            'std_score': 30,
            'std_avg_score': 10,
            'std_number': 20,
        }

    for i in range(0,len(firms)):
        firm = firms[i]
        firm.update({
            'avg_volume': round(firm['volume']/firm['number']),
            'avg_score': round(firm['score']*100/firm['number'])/100,
        })

        firm.update({
            'std_volume': volume_norm(firm['volume']),
            'std_avg_volume': avg_volume_norm(firm['avg_volume']),
            'std_score': score_norm(firm['score']),
            'std_avg_score': avg_score_norm(firm['avg_score']),
            'std_number': number_norm(firm['number']),
        })

        std_ova = firm['std_volume']*formula['std_volume'] + firm['std_avg_volume']*formula['std_avg_volume'] + \
                    firm['std_score']*formula['std_score'] + firm['std_avg_score']*formula['std_avg_score'] + \
                    firm['std_number']*formula['std_number']

        std_ova = std_ova / 100
        firm.update({ 'std_ova': std_ova })

    firms.sort(key=lambda x: (-x['std_ova'],-x['volume'],-x['score'],-x['number']))

    prc_firms = []
    global_firms = []
    for firm in firms:
        if firm['area'] == 1:   # PRC
            prc_firms.append(firm)
        else:
            global_firms.append(firm)

    now = datetime.datetime.now()
    tomorrow = datetime.datetime.strptime(now.strftime('%Y%m%d'),'%Y%m%d') + datetime.timedelta(days=1)
    timeout = int(tomorrow.timestamp() - now.timestamp())
    REDIS['app'].set('firm:rank:whole',json.dumps(firms),ex=timeout)
    REDIS['app'].set('firm:rank:prc',json.dumps(prc_firms),ex=timeout)
    REDIS['app'].set('firm:rank:global',json.dumps(global_firms),ex=timeout)



