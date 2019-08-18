# -*- coding: utf-8 -*-

import os,thriftpy

from core.utils.thrift import IDL_DIR
from core.utils.http import service

thriftpy.load(os.path.join(IDL_DIR, 'common.thrift'), module_name='common_thrift')
from common_thrift import OAuthService

thriftpy.load(os.path.join(IDL_DIR, 'law.thrift'), module_name='law_thrift')
from law_thrift import ConfigService, ClientService, FirmService, LawyerService, DealService, StatsService


routes = [
    # config
    { 'method': 'POST', 'path': '/law/config/load', 'handler': service(ConfigService,'load') },
    { 'method': 'POST', 'path': '/law/config/update', 'handler': service(ConfigService,'update') },

    # client
    { 'method': 'POST', 'path': '/law/client/filter', 'handler': service(ClientService,'filter') },
    { 'method': 'POST', 'path': '/law/client/create', 'handler': service(ClientService,'create') },
    { 'method': 'POST', 'path': '/law/client/{client}/update', 'handler': service(ClientService,'update') },
    { 'method': 'POST', 'path': '/law/client/{client}/remove', 'handler': service(ClientService,'remove') },
    { 'method': 'POST', 'path': '/law/client/{client}/digest', 'handler': service(ClientService,'get_digest') },
    { 'method': 'POST', 'path': '/law/client/{client}/detail', 'handler': service(ClientService,'get_detail') },

    # firm
    { 'method': 'POST', 'path': '/law/firm/filter', 'handler': service(FirmService,'filter') },
    { 'method': 'POST', 'path': '/law/firm/create', 'handler': service(FirmService,'create') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/update', 'handler': service(FirmService,'update') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/remove', 'handler': service(FirmService,'remove') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/digest', 'handler': service(FirmService,'get_digest') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/detail', 'handler': service(FirmService,'get_detail') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/children', 'handler': service(FirmService,'list_children') },

    { 'method': 'POST', 'path': '/law/firm/{firm}/feedback/filter', 'handler': service(FirmService,'filter_feedbacks') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/feedback/create', 'handler': service(FirmService,'create_feedback') },
    { 'method': 'POST', 'path': '/law/firm/{firm}/feedback/remove', 'handler': service(FirmService,'remove_feedback') },

    # lawyer
    { 'method': 'POST', 'path': '/law/lawyer/filter', 'handler': service(LawyerService,'filter') },
    { 'method': 'POST', 'path': '/law/lawyer/create', 'handler': service(LawyerService,'create') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/update', 'handler': service(LawyerService,'update') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/remove', 'handler': service(LawyerService,'remove') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/digest', 'handler': service(LawyerService,'get_digest') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/detail', 'handler': service(LawyerService,'get_detail') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/career', 'handler': service(LawyerService,'get_career') },

    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/feedback/filter', 'handler': service(LawyerService,'filter_feedbacks') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/feedback/create', 'handler': service(LawyerService,'create_feedback') },
    { 'method': 'POST', 'path': '/law/lawyer/{lawyer}/feedback/remove', 'handler': service(LawyerService,'remove_feedback') },

    # deal
    { 'method': 'POST', 'path': '/law/deal/filter', 'handler': service(DealService,'filter') },
    { 'method': 'POST', 'path': '/law/deal/create', 'handler': service(DealService,'create') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/update', 'handler': service(DealService,'update') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/remove', 'handler': service(DealService,'remove') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/digest', 'handler': service(DealService,'get_digest') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/detail', 'handler': service(DealService,'get_detail') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/relation', 'handler': service(DealService,'get_relation') },

    { 'method': 'POST', 'path': '/law/deal/{deal}/client/list', 'handler': service(DealService,'list_clients') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/client/add', 'handler': service(DealService,'add_client') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/client/update', 'handler': service(DealService,'update_client') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/client/remove', 'handler': service(DealService,'remove_client') },

    { 'method': 'POST', 'path': '/law/deal/{deal}/firm/list', 'handler': service(DealService,'list_firms') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/firm/add', 'handler': service(DealService,'add_firm') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/firm/update', 'handler': service(DealService,'update_firm') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/firm/remove', 'handler': service(DealService,'remove_firm') },

    { 'method': 'POST', 'path': '/law/deal/{deal}/lawyer/list', 'handler': service(DealService,'list_lawyers') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/lawyer/add', 'handler': service(DealService,'add_lawyer') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/lawyer/update', 'handler': service(DealService,'update_lawyer') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/lawyer/remove', 'handler': service(DealService,'remove_lawyer') },

    { 'method': 'POST', 'path': '/law/deal/{deal}/feedback/filter', 'handler': service(DealService,'filter_feedbacks') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/feedback/create', 'handler': service(DealService,'create_feedback') },
    { 'method': 'POST', 'path': '/law/deal/{deal}/feedback/remove', 'handler': service(DealService,'remove_feedback') },

    # stats
    { 'method': 'POST', 'path': '/law/stats/m1', 'handler': service(StatsService,'render_m1') },
    { 'method': 'POST', 'path': '/law/stats/m2', 'handler': service(StatsService,'render_m2') },

    { 'method': 'POST', 'path': '/law/stats/custom', 'handler': service(StatsService,'render_custom') },

    { 'method': 'POST', 'path': '/law/stats/ranking/firm', 'handler': service(StatsService,'list_ranking_firms') },
    { 'method': 'POST', 'path': '/law/stats/ranking/deal', 'handler': service(StatsService,'list_ranking_deals') },

    { 'method': 'POST', 'path': '/law/stats/firm/{firm}/recent', 'handler': service(StatsService,'analyse_recent_by_firm') },
    { 'method': 'POST', 'path': '/law/stats/lawyer/{lawyer}/recent', 'handler': service(StatsService,'analyse_recent_by_lawyer') },
]


