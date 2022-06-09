from scrapy.crawler import CrawlerProcess,  CrawlerRunner
from pathlib import Path
import os
from datetime import date
from scrapy.utils.project import get_project_settings

from articleScraperCeebios.spiders import (
    plos,
    biorxiv,
    nature
)

# https://www.pythonfixing.com/2022/04/fixed-scrapy-reactoralreadyinstallederr.html

p = Path(__file__)

settings = get_project_settings()
settings.update(
    {
        "MEDIA_ALLOW_REDIRECTS": True,
    }
)

# if "USERDOMAIN" in os.environ and os.environ["USERDOMAIN"] == 'JEAN-FRANCISSE':
#     settings.update(
#         {
#             "FILES_STORE": 'data/nature/files',
#             "IMAGES_STORE": 'data/nature/images',
#             "FEEDS": {
#                 "file:" + str(p.parent.joinpath(f"items{date.today().strftime('%d-%M-%Y')}.json")) : {"format": "jsonlines"},
#             },
#         }
#     )
# else:
settings.update(
    {
        "FEEDS": {
            "file:" + str(p.parent.joinpath(f"items{date.today().strftime('%d-%M-%Y')}.json")) : {"format": "jsonlines"},
            # f'gs://d4g-ceebios-bdd/raw_data/items{date.today().strftime("%d-%M-%Y")}.json': {"format": "jsonlines"},
        }, 
        "FILES_STORE": 'gs://d4g-ceebios-bdd/raw_data/',
        "IMAGES_STORE": 'gs://d4g-ceebios-bdd/images/'
    }
)

args = {
    "search":"species", 
    "begin_at":1, 
    "nb_article":10000
}
import sys

for spider in [plos.PlosSpider]:#,biorxiv.BiorxivSpider plos.PlosSpider, nature.Naturespider]:
    process = CrawlerProcess(settings)
    process.crawl(spider, **args)
    process.start() 


# deferred = process.join()
# deferred.addBoth(lambda _: reactor.stop())

# reactor.run() 
