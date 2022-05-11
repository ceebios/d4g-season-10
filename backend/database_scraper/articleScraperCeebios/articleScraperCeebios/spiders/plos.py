from cmath import log
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider
from ..items import ArticlescraperceebiosItem
import logging

# TODO: Arriver à récuprer le xml rediriger sur google, exemple: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0052337&type=manuscript
# ===> https://www.pythonfixing.com/2022/01/fixed-capture-redirect-response.html
# TODO: Scraper le js de plos 

class PlosSpider(Spider):
    
    name = 'plos'
    allowed_domains = ['journals.plos.org', "storage.googleapis.com", "api.plos.org"]
    ref_urls = {
        "SEARCH": """https://api.plos.org/search?q=everything:{}&fl=id,title&start={}&rows={}""",
        "ARTICLE": """https://journals.plos.org/plosone/article?id={}""",
    }
    custom_settings = {
        "ITEM_PIPELINES": {
            'scrapy.pipelines.images.FilesPipeline': 2,
            "articleScraperCeebios.pipelines_script.testPipe.SpiderOpenCloseLogging":1
        },
        "FILES_STORE": 'data/plos',
        "ROBOTSTXT_OBEY": False,
        "handle_httpstatus_all": True
    }


    def start_requests(self):
        tag        = getattr(self, 'search', "test")
        begin_at   = getattr(self, 'begin_at', 0)
        nb_article = getattr(self, 'nb_article', 10)
        if tag == "test":
            logging.log(logging.WARNING, "Attention on est en test car par d'argument trouvé")
        url = PlosSpider.ref_urls["SEARCH"].format(tag, begin_at, begin_at + nb_article)
        yield Request(url, self.parse_url) 

    def parse_url(self, response):
        jsonlist = response.json()
        jsonlist = jsonlist["response"]["docs"]
        for id_article in jsonlist:
            url_page = PlosSpider.ref_urls["ARTICLE"].format(id_article["id"])
            yield Request(
                url      = url_page,
                callback = self.parse
            )

    def parse(self, response):
        """Parse la réponse html de l'article

        :param response: _description_
        :type response: _type_
        :yield: _description_
        :rtype: _type_
        """
        logging.log(logging.INFO, "1 - Open Html page")
        article = ArticlescraperceebiosItem()
        article["name"] = response.css("h1#artTitle::text").get() ### Ici je ne suis pas sûre....
        article["title"] = response.css("h1#artTitle::text").get()
        article["url"] = response.url
        article["doi"] = response.css(
            "li#artDoi > a::text").get()
        article["abstract"] = response.css("div.abstract-content > *::text").extract()
        article["file_urls"] = [
            response.urljoin(
                response.css("a#downloadPdf::attr(href)").get()
            ),
            response.urljoin(
                response.css("a#downloadXml::attr(href)").get()
            )
        ]
        article["author"] = response.css("a.author-name::text").extract()
        article["date"] = response.css("li#artPubDate::text").get()
        yield article
        # response.url(
        #     url=response.urljoin(
        #             response.css("a#downloadXml::attr(href)").get()
        #         ),
        #     callback=self.parse_xml,
        #     meta=dict(item=article)
        # )

    def parse_xml(self, response):
        """Parse le XML de l'article

        :param response: Article en XML parser
        :type response: XmlResponse
        :yield: Item Article
        :rtype: ArticlescraperceebiosItem
        """
        logging.log(logging.INFO, "2 - Open XML file")
        article = response.meta["item"]
        article["journal"] = response.css("journal-id::text").get()
        article["publisher"] = response.css("publisher-name::text").get()
        article["type"] = response.css("subj-group *::text").get()
        article["content"] = response.text
        # yield article
