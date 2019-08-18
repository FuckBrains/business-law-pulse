# -*- coding: utf-8 -*-

# Scrapy settings for news project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html


from .const import CONST


BOT_NAME = 'news'
SPIDER_MODULES = [ 'news.spiders' ]
COMMANDS_MODULE = 'news.commands'

MEDIA_URL = CONST['storage']['url']['media']

USE_PROXY = CONST['proxies']['enabled']
SQUID_PROXIES = CONST['proxies']['squid']

DEVICES = CONST['devices']

#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
}

import mongoengine
for alias in CONST['mongo']:
    mongoengine.register_connection(
        alias,
        name=CONST['mongo'][alias]['db'],
        host=CONST['mongo'][alias]['host'],
        port=CONST['mongo'][alias]['port'],
        username=CONST['mongo'][alias]['username'],
        password=CONST['mongo'][alias]['password'],
    )

DEFAULT_OBJECTID = '0' * 24

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    #'scrapy.extensions.statsmailer.StatsMailer': None,
    #'scrapy.telnet.TelnetConsole': 0,
    #'scrapy.extensions.memusage.MemoryUsage': 0,
    #'scrapy.extensions.memdebug.MemoryDebugger': 0,
    #'scrapy.extensions.logstats.LogStats': 0,

    'scrapy.extensions.corestats.CoreStats': 0,
    'news.extensions.ExportStats': 10,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'news.pipelines.ValidateItemPipeline': 100,
    'news.pipelines.NewsPipeline': 200,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,

    'news.middlewares.UserAgentMiddleware': 100,
    'news.middlewares.ProxyMiddleware': 110,
    'news.middlewares.ExceptionMiddleware': 120,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 130,
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'news.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Configure maximum concurrent items (per response) processed by Scrapy (default: 100)
#CONCURRENT_ITEMS=100

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=16

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'


