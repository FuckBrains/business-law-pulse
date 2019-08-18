# -*- encoding: utf-8 -*-

from core.conf import CONST

#from core.utils.setup import setup_redis,setup_mongo
#setup_redis()
#setup_mongo()

import os
import argparse



class BaseCommand(object):
    def __init__(self):
        module,app = self.__module__.split('.')[:2]
        name = self.__class__.__name__
        filename = os.path.join(CONST['root'], 'log/%s.%s.%s.log' % (module,app,name))
        CONST['logging']['handlers']['command'].update({ 'filename': os.path.abspath(filename) })

        from logging.config import dictConfig
        dictConfig(CONST['logging'])

        import logging
        self.logger = logging.getLogger('command')

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        raise NotImplementedError

    def execute(self, argv):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)
        options = parser.parse_args(argv)
        options = vars(options)
        args = options.pop('args', ())
        self.handle(*args, **options)


