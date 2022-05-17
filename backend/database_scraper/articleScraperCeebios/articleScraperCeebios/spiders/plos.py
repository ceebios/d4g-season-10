import requests
from scrapy import Request
from scrapy.spiders import Spider
from ..items import ArticlescraperceebiosItem
import logging
import re

class PlosSpider(Spider):
    
    name = 'plos'
    allowed_domains = ['journals.plos.org', "storage.googleapis.com", "api.plos.org"]
    ref_urls = {
        "SEARCH": """https://api.plos.org/search?q=everything:{}&fl=id,title&start={}&rows={}""",
        "ARTICLE": """https://journals.plos.org/plosone/article?id={}""",
    }
    custom_settings = {
        "ITEM_PIPELINES": {
            'articleScraperCeebios.pipelines.XMLPipeline': 1,
            'articleScraperCeebios.pipelines.PDFPipeline': 2,
            'articleScraperCeebios.pipelines.figurePipline': 3
        },
        "handle_httpstatus_list":[302],
        "FILES_STORE": 'data/plos/files',
        "IMAGES_STORE": 'data/plos/images',

        # "IMAGES_STORE":'gs://d4g-ceebios-bdd/images/',
        # "FILES_STORE":'gs://d4g-ceebios-bdd/raw_data/',
        
        "ROBOTSTXT_OBEY": False
    }


    def start_requests(self):
        tag        = getattr(self, 'search', "test")
        begin_at   = getattr(self, 'begin_at', 0)
        nb_article = getattr(self, 'nb_article', 1)
        print(tag, begin_at, nb_article)
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
            )
        ]
        article["xml_urls"] = [
            response.urljoin(
                response.css("a#downloadXml::attr(href)").get()
            )
        ]

        article["author"] = response.css("a.author-name::text").extract()
        article["date"] = response.css("li#artPubDate::text").get()

        article["image_urls"] = [
            response.urljoin(imgs)
                for imgs in response.css("div.figure-inline-download > ul > li > a::attr(href)").getall()
                if re.search("image",imgs) and re.search("large",imgs)
            ]
        yield article
        # logging.log(logging.INFO, "2 -  Try to open file ")
        # print("#########################",response.urljoin(
        #             response.css("a#downloadXml::attr(href)").get()
        #         ))
        # response.url(
        #     url=response.urljoin(
        #             response.css("a#downloadXml::attr(href)").get()
        #         ),
        #     callback = self.parse_xml ,
        #     meta = dict(item=article)
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
