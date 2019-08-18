# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.command import BaseCommand

import os
import oss2


class UploadStatic(BaseCommand):
    def __init__(self):
        super(UploadStatic, self).__init__()

        self.config = CONST['oss']
        self.bucket = oss2.Bucket(
                        oss2.Auth(self.config['key_id'], self.config['key_secret']),
                        'http://%s' % self.config['host'],
                        self.config['bucket'])

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', default='static')
        parser.add_argument('--noreplace', dest='noreplace', action='store_true', default=False)

    def handle(self, *args, **options):
        if not options['path'] or options['path'].startswith('/'):
            print('Incorrect path')
            return

        self.logger.info('path : %s' % options['path'])
        self.upload(options['path'],options['noreplace'])
        print(flush=True)

    def upload(self, path, noreplace=False):
        filename = os.path.realpath(path)

        if os.path.isdir(filename):
            for item in os.listdir(filename):
                child_path = os.path.join(path,item)
                self.upload(child_path,noreplace)

        else:
            if noreplace and self.bucket.object_exists(path):
                return

            headers = {
                'Cache-Control': 'max-age=%s' % self.config['cache_age'],
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Max-Age': str(self.config['cache_age']),
                'Access-Control-Allow-Methods': ','.join(['POST','GET']),
                'Access-Control-Allow-Headers': ','.join(['Content-Type','AUTHORIZATION','X-Requested-With','X_Requested_With','*']),
            }

            print('.',end='',flush=True)
            return

            res = self.bucket.put_object_from_file(path,filename,headers=headers)
            if res.status == 200:
                print('.',end='',flush=True)
            else:
                print(flush=True)
                self.logger.error('fail : %s' % path)
                message = ''.join([seg.decode('utf8') for seg in res.readlines()])
                self.logger.error('message : %s' % message)


