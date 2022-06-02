# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import logging
import hashlib, os
from glob import glob
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import scrapy
from scrapy.utils.python import to_bytes
from bloom_filter import BloomFilter
import pickle


# class SelectItem:
#     def __init__(self, BLOOB_XML):
#         self.BLOOB_XML = BLOOB_XML

#     @classmethod
#     def from_crawler(cls, crawler):
#         ## pull in information from settings.py
#         return cls(
#             BLOOB_XML=crawler.settings.get('BLOOB_XML')
#         )
#     def accepts(self, item):
#         field = "doi" 
#         if field in item and not item[field] in self.lixml:
#             return True
#         return False

#     def open_spider(self, spider):
#         ## initializing spider
#         ## opening db connection
#         self.lixml = [file.split("/")[-1].split(".")[0] for file in glob(self.BLOOB_XML+"/*.xml")]
#         logging.log(1,self.lixml[0] )
        


class DoiPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('doi'):
            adapter['doi'] = adapter['doi'].replace("https://doi.org/", "").replace("/", "-")
            return item
        else:
            raise DropItem(f"Missing doi in {item}")


class XMLPipeline(FilesPipeline):
    MEDIA_NAME = "xml"
    DEFAULT_FILES_URLS_FIELD = 'xml_urls'
    DEFAULT_FILES_RESULT_FIELD = 'xmls'

    # def __init__(self, BLOOB_XML):
    #     self.BLOOB_XML = BLOOB_XML

    # @classmethod
    # def from_crawler(cls, crawler):
    #     ## pull in information from settings.py
    #     return cls(
    #         BLOOB_XML=crawler.settings.get('BLOOB_XML')
    #     )
    
    # def open_spider(self, spider):
    #     ## initializing spider
    #     ## opening db connection
    #     self.lixml = [file.split("/")[-1].split(".")[0] for file in glob(self.BLOOB_XML+"/*.xml")]
    #     logging.log(1,self.lixml[0] )

    # # Overridable Interface
    # def get_media_requests(self, item, info):
    #     urls = ItemAdapter(item).get(self.files_urls_field, [])
    #     doi = ItemAdapter(item).get("doi", [])
    #     return [scrapy.Request(u) for u in urls if not doi in self.lixml]

    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = item["doi"]
        return f'xml/{media_guid}.xml'

class PDFPipeline(FilesPipeline):
 
    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = item["doi"]
        return f'pdf/{media_guid}.pdf'
    
class figurePipline(ImagesPipeline):


    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = item["doi"] + "." + request.url.split(".")[-1]
        return f'{media_guid}.jpg'
