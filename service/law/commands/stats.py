# -*- coding: utf-8 -*-

from core.utils.command import BaseCommand

from core.utils.setup import setup_redis,setup_mongo
setup_redis()
setup_mongo()

from service.law.utils.stats import compute_firm_ranking



class ComputeFirmRanking(BaseCommand):
    def handle(self, *args, **options):
        compute_firm_ranking()





