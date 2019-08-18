# -*- coding: utf-8 -*-

from scrapy.conf import settings

import os,sys,json,datetime,time
import random,base64 
from six.moves.urllib.parse import urljoin

import logging
logger = logging.getLogger(__name__)



class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        random.seed(time.time())

        # Pick a random user agent from available list
        user_agent = settings['DEVICES']['pc'][random.randint(0,len(settings['DEVICES']['pc'])-1)]

        # Set the default user agent
        request.headers.setdefault('User-Agent', user_agent)



class ProxyMiddleware(object):
    def process_request(self, request, spider):
        if not settings['USE_PROXY']:
            return

        random.seed(time.time())

        # Pick a random proxy from available list
        proxy = settings['SQUID_PROXIES'][random.randint(0,len(settings['SQUID_PROXIES'])-1)]

        # Set the location of the proxy
        request.meta['proxy'] = 'http://%s:%s' % (proxy['host'],proxy['port'])
  
        ## Use the following lines if the proxy requires authentication
        #proxy_user_pass = '%s:%s' % (proxy['username'],proxy['password'])
        ## Setup basic authentication for the proxy
        #encoded_user_pass = base64.encodestring(proxy_user_pass)
        #request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass



class ExceptionMiddleware(object):
    def process_exception(self, request, exception, spider):
        return None





