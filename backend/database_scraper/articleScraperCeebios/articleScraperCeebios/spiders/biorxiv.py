import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ArticlescraperceebiosItem

## TODO: Faire une araignée avec une query de keyword: https://www.datasciencecentral.com/scrape-data-from-google-search-using-python-and-scrapy-step-by/

class BiorxivSpider(CrawlSpider):
    name = 'biorxiv'
    allowed_domains = ['www.biorxiv.org']
    start_urls = ['http://www.biorxiv.org/search/bigdata']

    custom_settings = {
        "ITEM_PIPELINES": {'scrapy.pipelines.images.FilesPipeline': 1},
        "FILES_STORE": 'data/biorxiv', 
        "ROBOTSTXT_OBEY": False
    }

    rules = (
        Rule(
            LinkExtractor(
                    restrict_css="a.highwire-cite-linked-title"
                ), 
            callback='parse'
        ),
    )

    def parse(self, response):
        self.start_urls = ["http://www.biorxiv.org"]

        article = ArticlescraperceebiosItem()
        article["name"]      = response.css("h1#page-title::text").get()
        article["title"]     = response.css("h1#page-title::text").get()
        article["url"]       = response.url
        article["doi"]       = response.css("span.highwire-cite-metadata-doi::text").get()
        ## TODO: Attention défaut à améliorer => nlm-given-names
        article["author"]    = response.css("span.highwire-citation-author *::text").extract()
        article["date"]      = response.css("div.pane-1 > div.pane-content::text").get()
        article["journal"]   = "biorxiv"
        article["publisher"] = "biorxiv"
        article["type"]      = "biologie"
        article["abstract"]  = response.css("p#p-2::text").extract()
        ## TIPS: Bien pensée à faire un objet url et non un str !
        article["file_urls"] = [response.urljoin(response.css("a.article-dl-pdf-link::attr(href)").get())]
        
        yield article
