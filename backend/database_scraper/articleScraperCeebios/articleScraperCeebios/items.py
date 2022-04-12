# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlescraperceebiosItem(scrapy.Item):
    # define the fields for your item here like:
    name      = scrapy.Field()
    title     = scrapy.Field()
    url       = scrapy.Field()
    doi       = scrapy.Field()
    author    = scrapy.Field()
    date      = scrapy.Field()
    journal   = scrapy.Field()
    publisher = scrapy.Field()
    type      = scrapy.Field()
    abstract  = scrapy.Field()
    
    ## Notre PDF ou XML
    file      = scrapy.Field()
    file_urls = scrapy.Field()
