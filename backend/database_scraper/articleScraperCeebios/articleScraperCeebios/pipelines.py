# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import hashlib, os
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

from scrapy.utils.python import to_bytes
import mimetypes

class ArticlescraperceebiosPipeline:
    def process_item(self, item, spider):
        return item


class XMLPipeline(FilesPipeline):
    MEDIA_NAME = "xml"
    DEFAULT_FILES_URLS_FIELD = 'xml_urls'
    DEFAULT_FILES_RESULT_FIELD = 'xmls'
    
    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'XML/{media_guid}.xml'

class PDFPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'PDF/{media_guid}.pdf'
    
class figurePipline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{media_guid}.jpg'
