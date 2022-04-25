from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider
from ..items import ArticlescraperceebiosItem
import logging

# TODO: Arriver à récuprer le xml rediriger sur google, exemple: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0052337&type=manuscript
# ===> https://www.pythonfixing.com/2022/01/fixed-capture-redirect-response.html
# TODO: Scraper le js de plos 

class BiorxivSpider(Spider):
    name = 'plos'
    allowed_domains = ['journals.plos.org', "storage.googleapis.com"]
    start_urls = ["https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0052337"]
    custom_settings = {
        "ITEM_PIPELINES": {'scrapy.pipelines.images.FilesPipeline': 1},
        "FILES_STORE": 'data/plos',
        "ROBOTSTXT_OBEY": False
    }

    # link_extractor = LinkExtractor(
    #     restrict_css="dt.search-results-title > a"
    # )

    # def start_requests(self):
    #     url = 'https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q='
    #     tag = getattr(self, 'search', None)
    #     if tag is not None:
    #         url = url + tag
    #     yield Request(url, self.parse_url)

    # def parse_url(self, response):
    #     for link in self.link_extractor.extract_links(response):
    #         yield Request(link.url, callback=self.parse)

    #     nb_page = getattr(self, 'num_pages', 2)
    #     NEXT_PAGE = response.css(
    #         "a#nextPageLink::attr(href)").get()
    #     NUM_PAGE = response.css("nav#article-pagination > a.active::text").get()
    #     # logging.log(logging.INFO, "")
    #     print(NUM_PAGE)
    #     if int(NUM_PAGE) <= int(nb_page):
    #         yield Request(
    #             url=response.urljoin(NEXT_PAGE),
    #             callback=self.parse_url
    #         )

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

        print(response.urljoin(
                    response.css("a#downloadXml::attr(href)").get()
                ))

        yield response.url(
            url=response.urljoin(
                    response.css("a#downloadXml::attr(href)").get()
                ),
            callback=self.parse_xml,
            meta=dict(item=article)
        )

    def parse_xml(self, response):
        """Parse le XML de l'article

        :param response: Article en XML parser
        :type response: XmlResponse
        :yield: Item Article
        :rtype: ArticlescraperceebiosItem
        """
        logging.log(logging.INFO, "3 - Open XML file")
        article = response.meta["item"]
        article["journal"] = response.css("journal-id::text").get()
        article["publisher"] = response.css("publisher-name::text").get()
        article["type"] = response.css("subj-group *::text").get()
        article["content"] = response.text
        yield article
