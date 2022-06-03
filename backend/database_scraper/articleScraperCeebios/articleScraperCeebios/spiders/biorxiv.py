from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider
from ..items import ArticlescraperceebiosItem
import logging

# TODO (maybe): Repo qui évite les mode inceptions: https://github.com/rmax/scrapy-inline-requests

class BiorxivSpider(CrawlSpider):
    name = 'biorxiv'
    allowed_domains = ['www.biorxiv.org', "api.biorxiv.org", "sass.highwire.org"]
    api = "https://api.biorxiv.org/details/biorxiv/"

    link_extractor = LinkExtractor(
        restrict_css="a.highwire-cite-linked-title"
    )

    def start_requests(self):
        url = 'https://www.biorxiv.org/'
        tag = getattr(self, 'search', None)
        if tag is not None:
            url = url + 'search/' + tag
        yield Request(url, self.parse_url)

    def parse_url(self, response):
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url+".full", callback=self.parse)
            break
        
        # nb_page = getattr(self, 'num_pages', 2)
        # NEXT_PAGE = response.css(
        #     "ul.pager-items-last > li > a::attr(href)").get()
        # if int(NEXT_PAGE.split("=")[-1]) <= int(nb_page):
        #     yield Request(
        #         url=response.urljoin(NEXT_PAGE), 
        #         callback=self.parse_url
        #     )

    def parse(self, response):
        """Parse la réponse html de l'article

        :param response: _description_
        :type response: _type_
        :yield: _description_
        :rtype: _type_
        """
        logging.log(logging.INFO, "1 - Open Html page:"+response.url)
        article = ArticlescraperceebiosItem()
        article["name"] = response.css("h1#page-title::text").get()
        article["title"] = response.css("h1#page-title::text").get()
        article["url"] = response.url
        article["doi"] = response.css(
            "span.highwire-cite-metadata-doi::text").get()
        article["abstract"] = response.css("p#p-2::text").extract()
        article["file_urls"] = [response.urljoin(
            response.css("a.article-dl-pdf-link::attr(href)").get())]
        article["image_urls"] = [
            response.urljoin(urlImg) for urlImg in response.css("li.download-fig > a::attr(href)").getall()
        ]
        yield response.follow(
            url=BiorxivSpider.api +
            article["doi"].replace(" https://doi.org/", "")[:-1],
            callback=self.parse_api,
            meta=dict(item=article)
        )

    def parse_api(self, response):
        """Parse la réponse json de l'api

        :param response: Le retour de l'api
        :type response: TextResponse
        """
        logging.log(logging.INFO, "2 - Open Json file")
        data = response.json()
        data = data["collection"][-1]

        article = response.meta["item"]
        article["author"] = data["authors"].split(";")
        article["date"] = data["date"]
        article["abstract"] = data["abstract"]

        
        article["xml_urls"] = [
            response.urljoin(data["jatsxml"])
        ]

        yield response.follow(
            url=data["jatsxml"],
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
        yield article
