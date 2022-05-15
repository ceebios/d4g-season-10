# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from io import BytesIO
from itemadapter import ItemAdapter
import os, re, requests
from scrapy.exceptions import DropItem
from contextlib import suppress
import scrapy

from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
# from pipelines.openSearchPipeline import OpenSearchDocumentStore
# from pipelines.testPipe import SpiderOpenCloseLogging

class ArticlescraperceebiosPipeline:
    def process_item(self, item, spider):
        return item


class FilePipeXML_PDF(FilesPipeline):

    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter['file_urls']:
            if re.search("manuscript",file_url): 
                return requests.get(file_url)
            else:
                yield scrapy.Request(file_url)


class ImageRedirectPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter['image_urls']:
            pic_redirect = requests.get(file_url)
            if len(pic_redirect.history) > 0:
                file_url = pic_redirect.url
            yield scrapy.Request(file_url)

    def item_completed(self, results, item, info):
        temp_treatment = [requests.get(x) for x in item['image_urls']]
        with suppress(KeyError):
            ItemAdapter(item)[self.images_result_field] = [x.content for x in temp_treatment if len(x.history) > 0]
        return item