from .base import Article, Meta, Retriever, HOME
from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests

URL = {
    "search": """https://www.biorxiv.org/search/{}%20numresults%3A{}%20sort%3Arelevance-rank{}""",
    "base": "https://www.biorxiv.org",
    "api": "https://api.biorxiv.org/details/biorxiv/",
}


class Biorxiv(Retriever):
    def __init__(self, location=HOME) -> None:
        super().__init__(journal="biorxiv", URL=URL, location=location)

    def get_search_url(self, query, page, page_size):
        if page == 0:
            return self.URL["search"].format(quote(query), page_size, "")
        else:
            return self.URL["search"].format(
                quote(query), page_size, "?page=" + str(page)
            )

    def init_metas(self, soup: BeautifulSoup) -> list[Meta]:
        metas = []
        links = soup.find_all("a", {"class": "highwire-cite-linked-title"})
        dois = soup.find_all("span", {"class": "highwire-cite-metadata-doi"})
        for link, doi in zip(links, dois):
            uri = link.get("href") + ".full"
            metas.append(
                Meta(
                    title=link.text,
                    url=URL["base"] + uri,
                    doi=list(doi.children)[1].text.strip(),
                )
            )
        return metas

    def _search(self, query, page, page_size) -> list[Meta]:
        url = self.get_search_url(query, page, page_size)
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urlopen(req)
        soup = BeautifulSoup(res.read(), "lxml")
        metas = self.init_metas(soup)
        return metas

    def parse_body(self, section):
        if section.name == "p":
            return [section.text]
        if section.name == "fig":
            title = "figure" if not section.title else section.title.text
            return [{"title": title, "text": [p.text for p in section.find_all("p")]}]
        if section.name == "table-wrap":
            title = "table" if not section.title else section.title.text
            return [{"title": title, "text": [p.text for p in section.find_all("p")]}]
        if section.name in ["supplementary-material", "disp-formula"]:
            return []
        if section.name == "sec":
            text, title = [], ""
            for child in section.children:
                if child.name == "title":
                    title = child.text
                else:
                    tmp = self.parse_body(child)
                    if tmp:
                        text.append(tmp)
            if text:
                return [{"title": title, "text": sum(text, [])}]
            else:
                return []
        if type(section) == NavigableString:
            return []
        return sum(
            [self.parse_body(child) for child in section.children if child.text], []
        )

    def parse_article(self, meta: Meta) -> Article:
        api = self.URL["api"] + meta.doi.replace("https://doi.org/", "")
        data = requests.get(api).json()["collection"][-1]
        meta.author = data["authors"].split(";")
        meta.date = data["date"]
        meta.abstract = data["abstract"]
        meta.pdf = meta.url.replace(".full", ".pdf")

        req = Request(data["jatsxml"], headers={"User-Agent": "Mozilla/5.0"})
        res = urlopen(req)
        xml = res.read()
        soup = BeautifulSoup(xml, "xml")

        meta.publisher = soup.find("publisher-name").text
        meta.journal = soup.find("journal-id").text
        meta.type = soup.find("subj-group", {"subj-group-type": "author-type"}).text

        text = self.parse_body(soup.body)

        return Article(meta=meta, ajson=text, axml=xml)
