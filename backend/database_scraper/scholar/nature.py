from bs4 import BeautifulSoup
from .base import Article, Meta, Retriever, HOME
from urllib.parse import quote
from urllib.request import Request, urlopen

URL = {
    "base": "https://www.nature.com",
    "search": "https://www.nature.com/search?q={}&journal=srep,%20ismej,%20ncomms&order=relevance{}",
}


class Nature(Retriever):
    def __init__(self, location=HOME) -> None:
        super().__init__(journal="nature", URL=URL, location=location)
        self.meta = {
            "author": "dc.creator",
            "date": "dc.date",
            "doi": "citation_doi",
            "journal": "citation_journal_title",
            "publisher": "citation_publisher",
            "type": "citation_article_type",
            "pdf": "citation_pdf_url",
        }

    def get_search_url(self, query, page, page_size):
        if page == 0:
            return self.URL["search"].format(quote(query), "")
        else:
            return self.URL["search"].format(quote(query), "?page=" + str(page + 1))

    def _search(self, query, page, page_size) -> list[Meta]:
        url = self.get_search_url(query, page, page_size)
        html = urlopen(url).read().decode("utf-8")
        soup = BeautifulSoup(html, "lxml")
        metas = []
        for article in soup.find_all("article"):
            link = article.find("a")
            uri = link.get("href")
            metas.append(Meta(title=link.text, url=self.URL["base"] + uri, doi=""))
        return metas

    def parse_article(self, meta: Meta) -> Article:
        html = urlopen(meta.url).read().decode("utf-8")
        soup = BeautifulSoup(html, "lxml")
        for k, v in self.meta.items():
            els = soup.find_all("meta", {"name": v})
            els = [el.get("content") for el in els]
            if len(els) == 1:
                meta.__setattr__(k, els[0])
            else:
                meta.__setattr__(k, els)
        meta.abstract = soup.find("div", {"id": "Abs1-content"}).p.text
        body = soup.find("div", {"class": "c-article-body"})
        if not body:
            body = soup.find("article")

        text = self.get_sections(body)
        return Article(meta=meta, ajson=text, axml=soup.prettify())

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
