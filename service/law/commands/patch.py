# -*- coding: utf-8 -*-

from core.utils.command import BaseCommand

from core.utils.setup import setup_redis,setup_mongo
setup_redis()
setup_mongo()



class PatchData(BaseCommand):
    def handle(self, *args, **options):
        pass


