from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from articleScraperCeebios.spiders import (
    nature,
    biorxiv,
    plos
)


settings = get_project_settings()
process = CrawlerProcess(settings)
process.crawl(plos.PlosSpider)
# process.crawl(MySpider2)

process.start() # the script will block here until all crawling jobs are finished