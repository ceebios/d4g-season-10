# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from urllib.parse import urlparse

from scrapy.pipelines.files import FilesPipeline
# from pipelines.openSearchPipeline import OpenSearchDocumentStore
# from pipelines.testPipe import SpiderOpenCloseLogging

class ArticlescraperceebiosPipeline:
    def process_item(self, item, spider):
        return item

