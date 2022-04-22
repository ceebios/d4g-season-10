from .base import Article, Meta, Retriever, HOME
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from requests_html import HTMLSession

session = HTMLSession()


# The Royal Society Publishing
URL = {
    "base": "https://royalsocietypublishing.org",
    "search": "https://royalsocietypublishing.org/action/doSearch?AllField={}&sortBy=relevancy{}",
}


class RoyalSociety(Retriever):
    def __init__(self, location=HOME) -> None:
        super().__init__(journal="royal_society", URL=URL, location=location)

    def get_search_url(self, query, page):
        if page:
            return self.URL["search"].format(quote(query), "&startPage=" + str(page))
        else:
            return self.URL["search"].format(quote(query), "")

    def get_page_html(self, url):
        res = session.get(url)
        res.html.render(wait=1, sleep=1)
        html = res.html.html
        return html

    def init_metas(self, page_soup):
        metas = []
        articles = page_soup.find_all(
            "li", {"class": "clearfix separator search__item"}
        )
        for article in articles:
            link = uri = article.find("a", {"title": "Full text"})
            if link:
                title = re.sub(
                    "[\n ]+",
                    " ",
                    article.find("span", {"class": "hlFld-Title"}).find("a").text,
                )
                doi = article.find("a", {"class": "meta__doi"}).get("href")
                uri = link.get("href")
                metas.append(Meta(title=title, url=self.URL["base"] + uri, doi=doi))
        return metas

    def _search(self, query, page, page_size) -> list[Meta]:
        url = self.get_search_url(query, page)
        html = self.get_page_html(url)
        soup = BeautifulSoup(html, "lxml")
        metas = self.init_metas(soup)
        return metas

    def get_meta(self, meta, page_soup) -> Meta:
        article = page_soup.find("div", {"class": "article-data"})
        # Add authors
        authors = article.find_all("span", {"class": "hlFld-ContribAuthor"})
        meta.author = [a.text for a in authors]
        meta.date = page_soup.find("span", {"class": "epub-section__date"}).text
        meta.publisher = "The Royal Society"
        meta.journal = (
            page_soup.find("div", {"class": "row col-md-12"}).find("img").get("alt")
        )
        doi_short = meta.doi.replace("https://doi.org", "")
        meta.pdf = self.URL["base"] + "/doi/pdf" + doi_short
        meta.url = self.URL["base"] + "/doi/full" + doi_short
        meta.type = page_soup.find(
            "span", {"class": "citation__top__item article__tocHeading"}
        ).text
        meta.abstract = page_soup.find(
            "div", {"class": "abstractSection abstractInFull"}
        ).text
        return meta

    def get_sections(self, soup, level=0):
        abstract = soup.find("div", {"class": "hlFld-Abstract"})
        body = soup.find("div", {"class": "hlFld-Fulltext"})
        return self._get_sections(abstract) + self._get_sections(body, level=1)

    def _get_sections(self, soup, level=0):
        sections = soup.find_all(self.levels[level])
        try:
            sections = [
                sec for sec in sections if "table-collapser" not in sec.get("class")[0]
            ]
        except:
            x = 0
        if len(sections) == 0 and level < 4:
            return self._get_sections(soup, level + 1)
        if len(sections) == 0:
            return None
        if level == 4:
            return [s.text for s in sections if s.text if s.text]
        else:
            parse = []
            for i in range(len(sections)):
                parent = str(soup)
                start = str(sections[i])
                div = parent[parent.rfind(start) :]
                if i == len(sections) - 1:
                    div = BeautifulSoup(div, "lxml")
                else:
                    end = str(sections[i + 1])
                    div = BeautifulSoup(div[: div.rfind(end)], "lxml")
                part = {
                    "title": sections[i].text,
                    "text": self._get_sections(div, level + 1),
                }
                if part["text"]:
                    parse.append(part)
            return parse

    def parse_article(self, meta: Meta) -> Article:
        html = self.get_page_html(meta.url)
        soup = BeautifulSoup(html, "lxml")
        meta = self.get_meta(meta, soup)
        text = self.get_sections(soup)
        return Article(meta=meta, ajson=text, axml=html)
