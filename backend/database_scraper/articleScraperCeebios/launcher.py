from scrapy.crawler import CrawlerProcess
from pathlib import Path
import os
from datetime import date
from scrapy.utils.project import get_project_settings

from articleScraperCeebios.spiders import (
    plos
)

p = Path(__file__)

settings = get_project_settings()
settings.update(
    {
        "MEDIA_ALLOW_REDIRECTS": True,
    }
)

if os.environ["USERDOMAIN"] == 'JEAN-FRANCISSE' and False:
    settings.update(
        {
            "FILES_STORE": 'data/plos/files',
            "IMAGES_STORE": 'data/plos/images',
            "FEEDS": {
                "file:" + str(p.parent.joinpath(f"items{date.today().strftime('%d-%M-%Y')}.json")) : {"format": "jsonlines"},
            },
        }
    )
else:
    settings.update(
        {
            "FEEDS": {
                f'gs://d4g-ceebios-bdd/raw_data/items25-00-2022.json': {"format": "json"},
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

process = CrawlerProcess(settings)
process.crawl(plos.PlosSpider, **args)

process.start() 