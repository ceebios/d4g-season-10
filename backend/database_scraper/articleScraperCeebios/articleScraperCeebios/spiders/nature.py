from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ArticlescraperceebiosItem
from scrapy import Request
import logging
from scrapy.utils.response import open_in_browser

class Naturespider(CrawlSpider):
    name = 'nature'
    allowed_domains = ['www.nature.com', "idp.nature.com"]
    ref_urls = {
        "SEARCH":"""https://www.nature.com/search?q={}&article_type=research&order=relevance""",
        "SEARCH_FILTER": """"https://www.nature.com/search?q={}&date_range=last_30_days&order=relevance"""
        }
    link_extractor = LinkExtractor(
            restrict_xpaths='//h3[@class="c-card__title"]'
    )
    
    def start_requests(self):
        tag = getattr(self, 'search', "species")
        if tag is not None:
            url = self.ref_urls["SEARCH"].format(tag)
        yield Request(url, self.parse_url, dont_filter = True)

    def parse_url(self, response):
        logging.log(logging.INFO, "Open Links")
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse)
        
        nb_page = getattr(self, 'num_pages', 2)
        NEXT_PAGE = response.xpath("//li[@data-page='next']/a/@href").get()
        if int(NEXT_PAGE.split("=")[-1]) <= int(nb_page):
            yield Request(
                url=response.urljoin(NEXT_PAGE), 
                callback=self.parse_url
            )

    def parse(self, response):
        """Parse la réponse html de l'article

        :param response: _description_
        :type response: _type_
        :yield: _description_
        :rtype: _type_
        """
        logging.log(logging.INFO, "Get Item")
        
        article = ArticlescraperceebiosItem()
        article["name"]      = response.xpath('//*[@class="c-article-title"]/text()').get()
        article["title"]     = response.xpath('//*[@class="c-article-title"]/text()').get()
        article["url"]       = response.url
        article["doi"]       = response.xpath('//*[@class="c-bibliographic-information__list-item c-bibliographic-information__list-item--doi"]/p/span[@class="c-bibliographic-information__value"]/text()').get()
        article["abstract"]  = response.xpath('//*[@id="Abs1-content"]/p/text()').get()

        article["file_urls"] = [response.urljoin(response.css("a.c-pdf-download::attr(href)").get()) + ".pdf"] 
        article["author"]    = response.xpath('//*[@data-test="author-name"]/text()').extract()
        article["date"]      = response.xpath('//*[@class="c-article-identifiers__item"]/a/time/text()').get()

        article["journal"]   = response.xpath('//*[@class="c-article-info-details"]/a/i/text()').get()
        article["publisher"] = "nature"
        article["image_urls"] = [
            response.urljoin(urlImg) for urlImg in response.css("a.c-article-section__figure-link > picture > source > img::attr(src)").getall()
        ]
        if len(article["image_urls"]) > 0:
            pass
            # yield article
