from bs4 import BeautifulSoup
from .base import Article, Meta, Retriever, HOME
from urllib.parse import quote
import requests
from bs4.element import NavigableString

URL = {
    "search": """http://api.plos.org/search?q=everything:{}&fl=id,title&start={}&rows={}""",
    "article": """http://journals.plos.org/plosone/article/file?id={}&type=manuscript""",
    "link": """http://journals.plos.org/plosone/article?id={}""",
    "pdf": """http://journals.plos.org/plosone/article/file?id={}&type=printable""",
}


class PLOS(Retriever):
    def __init__(self, location=HOME) -> None:
        super().__init__(journal="plos", URL=URL, location=location)
        self.sleep = 6

    def _search(self, query, page, page_size) -> list[Meta]:
        url = URL["search"].format(
            quote(query), 1 + page * page_size, (1 + page) * page_size
        )
        res = requests.get(url).json()["response"]
        metas = [
            Meta(
                title=doc["title"], doi=doc["id"], url=URL["article"].format(doc["id"])
            )
            for doc in res["docs"]
        ]
        return metas

    def get_text(self, soup, field, filter=None):
        if filter:
            c = soup.find(field, filter)
        else:
            c = soup.find(field)
        if c:
            return c.text
        else:
            return ""

    def parse_article(self, meta: Meta) -> Article:
        res = requests.get(meta.url)
        soup = BeautifulSoup(res.text, "lxml")
        front = soup.find("front")
        meta.journal = self.get_text(front, "journal-title")
        meta.publisher = self.get_text(front, "publisher-name")
        meta.type = front.find(
            "subj-group", {"subj-group-type": "heading"}
        ).subject.text
        authors = front.find_all("contrib", {"contrib-type": "author"})
        meta.author = [
            a.find("given-names").text + " " + a.surname.text for a in authors
        ]
        date = front.find("pub-date", {"pub-type": "epub"})
        meta.date = "{}-{}-{}".format(date.year.text, date.month.text, date.day.text)
        meta.url = self.URL["link"].format(meta.doi)
        meta.pdf = self.URL["pdf"].format(meta.doi)
        meta.abstract = front.abstract.text.replace("\n", " ").strip()
        body = soup.body
        text = self.parse_body(body)
        return Article(meta=meta, ajson=text, axml=res.text)

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
