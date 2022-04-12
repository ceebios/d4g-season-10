from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ArticlescraperceebiosItem
import json

# TODO: Faire une araignée avec une query de keyword: https://www.datasciencecentral.com/scrape-data-from-google-search-using-python-and-scrapy-step-by/
# => ,Chercher plutot dans les bests practices
# Scrapy à la inception: https://stackoverflow.com/questions/36947822/scrapy-data-in-the-same-item-from-multiple-link-in-the-same-page        
# Repo qui évite les mode inceptions: https://github.com/rmax/scrapy-inline-requests
        


class BiorxivSpider(CrawlSpider):
    name = 'biorxiv'
    allowed_domains = ['www.biorxiv.org', "api.biorxiv.org"]
    start_urls = ['http://www.biorxiv.org/search/bigdata']
    api = "https://api.biorxiv.org/details/biorxiv/"

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

    # def start_requests(self):
    #     url = 'https://www.biorxiv.org/'
    #     tag = getattr(self, 'search', None)
    #     if tag is not None:
    #         url = url + 'search/' + tag
    #     yield Request(url, self.parse)


    def parse(self, response):
        """Parse la réponse html de l'article

        :param response: _description_
        :type response: _type_
        :yield: _description_
        :rtype: _type_
        """
        article = ArticlescraperceebiosItem()
        article["name"]      = response.css("h1#page-title::text").get()
        article["title"]     = response.css("h1#page-title::text").get()
        article["url"]       = response.url
        article["doi"]       = response.css("span.highwire-cite-metadata-doi::text").get()
        article["abstract"]  = response.css("p#p-2::text").extract()
        ## TIPS: Bien pensée à faire un objet url et non un str !
        article["file_urls"] = [response.urljoin(response.css("a.article-dl-pdf-link::attr(href)").get())]
        
        yield response.follow(
            url = BiorxivSpider.api + article["doi"].replace(" https://doi.org/", "")[:-1], 
            callback = self.parse_api, 
            meta = dict(item=article)
            )

    def parse_api(self, response):
        """Parse la réponse json de l'api

        :param response: Le retour de l'api
        :type response: TextResponse
        """
        print(type(response))
        data = json.loads(response.text)
        data = data["collection"][-1]
        
        article = response.meta["item"]
        article["author"]    = data["authors"].split(";")
        article["date"]      = data["date"]
        article["abstract"]  = data["abstract"]
        article["file_urls"] += [response.urljoin(data["jatsxml"])] 
        
        yield response.follow(
            url = data["jatsxml"], 
            callback = self.parse_xml, 
            meta = dict(item=article)
            )

    def parse_xml(self, response):
        """Parse le XML de l'article

        :param response: Article en XML parser
        :type response: XmlResponse
        :yield: Item Article
        :rtype: ArticlescraperceebiosItem
        """
        
        article = response.meta["item"]
        article["journal"]   = response.css("journal-id::text").get()
        article["publisher"] = response.css("publisher-name::text").get()
        article["type"]      = response.css("subj-group *::text").get() # data["category"] # response.xpath("//subj-group[contains(@subj-group-type:'author-type')]")
        yield article
