from xml.etree import ElementTree as ET
from .base import Article, Meta, Retriever, HOME
from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests
from . import keys
import pandas

URL = {
    "search": "http://api.springernature.com/meta/v2/json?q={} openaccess:true&p={}&s={}&api_key="
    + keys.nature
}


class Springer(Retriever):
    def __init__(self, location=HOME) -> None:
        super().__init__(journal="springer", URL=URL, location=location)

    def get_search_url(self, query, page, page_size) -> str:
        return self.URL["search"].format(quote(query), page_size, 1 + page * page_size)

    def init_meta(self, item) -> Meta:
        links = pandas.DataFrame(item["url"])
        url = links[links["format"] == "html"]["value"].values[0]
        pdf = links[links["format"] == "pdf"]["value"].values[0]
        return Meta(
            title=item["title"],
            url=url,
            doi=item["doi"],
            author=[c["creator"] for c in item["creators"]],
            date=item["onlineDate"],
            journal=item["publicationName"],
            publisher=item["publisher"],
            pdf=pdf,
            type=item["contentType"],
            abstract=item["abstract"],
        )

    def _search(self, query, page, page_size) -> list[Meta]:
        url = self.get_search_url(query, page, page_size)
        res = requests.get(url)
        items = res.json()["records"]
        metas = [self.init_meta(item) for item in items]
        return metas

    def get_sections(self, soup, level=0):
        sections = soup.find_all(self.levels[level])
        if len(sections) == 0 and level < 4:
            return self.get_sections(soup, level + 1)
        if len(sections) == 0:
            return None
        if level == 4:
            return [s.text for s in sections if s.text]
        else:
            parse = []
            sections = [section for section in sections if section.get("id")]
            for i in range(len(sections)):
                div = soup.find_all("div", {"id": sections[i].get("id") + "-content"})
                if not div:
                    parent = str(sections[i].parent)
                    start = str(sections[i])
                    div = parent[parent.rfind(start) :]
                    if i == len(sections) - 1:
                        div = BeautifulSoup(div, "lxml")
                    else:
                        end = str(sections[i + 1])
                        div = BeautifulSoup(div[: div.rfind(end)], "lxml")
                else:
                    div = div[0]
                part = {
                    "title": sections[i].text,
                    "text": self.get_sections(div, level + 1),
                }
                if part["text"]:
                    parse.append(part)
            return parse

    def parse_article(self, meta: Meta) -> Article:
        if "openurl" in meta.url:
            res = requests.get(meta.url)
            url = res.url
        else:
            url = meta.url
        html = urlopen(url).read().decode("utf-8")
        soup = BeautifulSoup(html, "lxml")
        meta.journal = soup.find("meta", {"name": "citation_journal_title"}).get(
            "content"
        )

        body = soup.find("div", {"class": "c-article-body"})
        if not body:
            body = soup.find("article")

        text = self.get_sections(body)

        return Article(meta=meta, ajson=text, axml=soup.prettify())
