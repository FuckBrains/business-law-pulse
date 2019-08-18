# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.command import BaseCommand

from core.utils.setup import setup_redis,setup_mongo
setup_redis()
setup_mongo()

import json,datetime
import subprocess

from service.law.models import LawConfig

CONFIG = CONST['mongo']['primary']
COLLECTIONS = [
    'law_config','law_exchange_currency','law_exchange_history',
    'law_client','law_firm','law_lawyer','law_deal',
]



class ExportData(BaseCommand):
    def handle(self, *args, **options):
        subprocess.call('rm -rf mongo && mkdir -p mongo', shell=True)

        tpl = "/usr/local/mongodb/bin/mongoexport -h %s:%s -u %s -p %s --db %s -c %s -o mongo/%s/%s.json"
        for collection in COLLECTIONS:
            cmd = tpl % (CONFIG['host'], CONFIG['port'], CONFIG['username'], CONFIG['password'], CONFIG['db'], collection, CONFIG['db'], collection)
            subprocess.call(cmd, shell=True)

        subprocess.call('rm -rf mongo.tar.bz2 && tar jcf mongo.tar.bz2 mongo && rm -rf mongo', shell=True)



class ImportData(BaseCommand):
    def handle(self, *args, **options):
        subprocess.call('ssh michael@blp.liangyongxiong.cn "cd ~/workspace/blp; python3 manage.py service law command ExportData"', shell=True)
        subprocess.call('scp michael@blp.liangyongxiong.cn:~/workspace/blp/mongo.tar.bz2 .', shell=True)
        subprocess.call('tar xf mongo.tar.bz2 && rm -rf mongo.tar.bz2', shell=True)

        tpl = "mongoimport -h %s:%s -u %s -p %s -d %s -c %s --file mongo/%s/%s.json --drop"
        for collection in COLLECTIONS:
            cmd = tpl % (CONFIG['host'], CONFIG['port'], CONFIG['username'], CONFIG['password'], CONFIG['db'], collection, CONFIG['db'], collection)
            subprocess.call(cmd, shell=True)

        configs = LawConfig.objects.filter(key__in=['categories','industries','areas','parties','roles'])
        for config in configs:
            REDIS['app'].set('law:config:%s' % config.key, json.dumps(config.value))

        subprocess.call('rm -rf mongo', shell=True)
        subprocess.call('ssh michael@blp.liangyongxiong.cn "cd ~/workspace/blp; rm -f mongo.tar.bz2"', shell=True)



class BackupData(BaseCommand):
    def handle(self, *args, **options):
        timestamp = datetime.datetime.now().strftime('%m-%dT%H-%M')
        subprocess.call('rm -rf mongo-%s && mkdir -p mongo-%s' % (timestamp,timestamp), shell=True)

        tpl = "/usr/local/mongodb/bin/mongoexport -h %s:%s -u %s -p %s --db %s -c %s -o mongo-%s/%s/%s.json"
        for collection in COLLECTIONS:
            cmd = tpl % (CONFIG['host'], CONFIG['port'], CONFIG['username'], CONFIG['password'], CONFIG['db'], collection, timestamp, CONFIG['db'], collection)
            subprocess.call(cmd, shell=True)

        subprocess.call('rm -rf mongo-%s.tar.bz2 && tar jcf mongo-%s.tar.bz2 mongo-%s && rm -rf mongo-%s' % (timestamp,timestamp,timestamp,timestamp), shell=True)
        subprocess.call('mv mongo-%s.tar.bz2 media' % timestamp, shell=True)



