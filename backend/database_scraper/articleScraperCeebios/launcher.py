from scrapy.crawler import CrawlerProcess
from pathlib import Path
from scrapy.utils.project import get_project_settings
from articleScraperCeebios.spiders import (
    nature,
    biorxiv,
    plos
)

p = Path(__file__)

settings = get_project_settings()
settings.update(
    {
        "FEEDS": {
            # "gs://d4g-ceebios-bdd/raw_data/items.json": {"format": "json"},
            str(p.parent.joinpath("items.json")) : {"format": "json"},
        },
    }
)

args = {
    "search":"bio", 
    "begin_at":1, 
    "nb_article": 1
}

process = CrawlerProcess(settings)
process.crawl(plos.PlosSpider, **args)

process.start() 