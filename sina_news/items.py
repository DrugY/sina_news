# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    time = scrapy.Field()
    subtitle = scrapy.Field()
    article = scrapy.Field()
    images = scrapy.Field()
    comments = scrapy.Field()
