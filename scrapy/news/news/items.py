# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:

    entry = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    cover = scrapy.Field()
    published = scrapy.Field()

    content = scrapy.Field()
    summary = scrapy.Field()

    def digest(self):
        return {
            'entry': self.get('entry',''),
            'url': self.get('url',''),
            'title': self.get('title',''),
        }



