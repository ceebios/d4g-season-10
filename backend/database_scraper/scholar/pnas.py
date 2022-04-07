from .base import Article, Meta, Retriever, HOME
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import requests

#from selenium import webdriver
#from selenium.webdriver.edge.options import Options
#options = Options()
#options.add_argument("--headless")
#driver = webdriver.Edge(options=options)

from requests_html import HTMLSession
session = HTMLSession()

URL = {
    "base": "https://www.pnas.org/",
    "_old_search": "https://www.pnas.org/search/{}%20content_type%3Ajournal%20flag%3AOPENACCESS%20numresults%3A{}%20sort%3Arelevance-rank?page={}",
    "search":"https://www.pnas.org/action/doSearch?field1=AllField&text1={}&publication=&Ppub=&access=on"
}


class PNAS(Retriever):
    def __init__(self, location=HOME) -> None:
        assert 0==1, 'PNAS has blocked scrapin'
        super().__init__(journal="pnas", URL=URL, location=location)
        self.meta = {
            "author": "citation_author",
            "date": "DC.Date",
            "publisher": "citation_publisher",
            "journal": "citation_journal_title",
            "pdf": "citation_pdf_url",
            "url": "citation_full_html_url",
        }


    def get_search_url(self, query, page, page_size):
        if page:
            return self.URL["search"].format(
                quote(query.replace(' ','+')), page_size, "&page=" + str(page)
            )
        else:
            return self.URL["search"].format(quote(query), page_size, "")

    def init_metas(self, page_soup):
        article_links = []
        cards = page_soup.find_all("div", {"class": "card-content"})
        for article in cards:
            access = article.find("div", {"class": "highwire-cite-access"}).text
            if access in ["You have access", "Open Access"]:
                a = article.find("a", {"class": "highwire-cite-linked-title"})
                uri = a.get("href")
                title = a.text
                links = article.find_all("a")
                doi = [
                    a.get("href") for a in links if "https://doi.org" in a.get("href")
                ][0]
                article_links.append(
                    Meta(title=title, url=self.URL["base"] + uri, doi=doi)
                )
        return article_links

    def get_page_html(self, url):
        res = session.get(url)
        res.html.render(wait=5, sleep=1)
        html = res.html.html
        #html = driver.get(url).page_source
        #driver.quit()
        return html

    def _search(self, query, page, page_size) -> list[Meta]:
        url = self.get_search_url(query, page, page_size)
        print(url)
        breakpoint()
        #html = requests.get(url).text
        html = self.get_page_html(url)
        soup = BeautifulSoup(html, "lxml")
        return self.init_metas(soup)

    def get_sections(self, soup, level=0):
        sections = soup.find_all(self.levels[level])
        if len(sections) == 0 and level < 4:
            return self.get_sections(soup, level + 1)
        if len(sections) == 0:
            return None
        if level == 4:
            return [s.text for s in sections if s.text]
        else:
            out = []
            for sec in sections:
                part = {
                    "title": sec.text,
                    "text": self.get_sections(sec.parent, level + 1),
                }
                if part["text"]:
                    out.append(part)
            return out

    def get_meta(self, meta, page_soup) -> Meta:
        for k, v in self.meta.items():
            els = page_soup.find_all("meta", {"name": v})
            els = [el.get("content") for el in els]
            if len(els) == 1:
                meta.__setattr__(k, els[0])
            else:
                meta.__setattr__(k, els)
        meta.type = page_soup.find(
            "span",
            {"class": "highwire-cite-metadata-article-category highwire-cite-metadata"},
        ).text
        meta.abstract = (
            page_soup.find("meta", {"name": "citation_abstract"})
            .get("content")
            .replace("<p>", "")
        )
        return meta

    def parse_article(self, meta: Meta) -> Article:
        html = requests.get(meta.url).text
        soup = BeautifulSoup(html, "lxml")
        meta = self.get_meta(meta, soup)
        text = self.get_sections(soup)
        return Article(meta=meta, ajson=text, axml=soup.prettify())
