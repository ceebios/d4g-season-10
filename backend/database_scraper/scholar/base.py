import os
import json
import re
from tqdm import tqdm
from urllib import request, parse
import time
import re
from bs4 import BeautifulSoup

HOME = os.environ.get("DATAHOME", os.path.join(os.path.expanduser("~"), "articles"))
toname = lambda x: re.sub(r"[^a-zA-Z0-9 ]", "", x)


class Meta(object):
    def __init__(
        self,
        title: str,
        url: str,
        doi: str,
        author: list[str] = [],
        date: str = "",
        journal: str = "",
        publisher: str = "",
        pdf: str = "",
        type: str = "",
        abstract: str = "",
    ):
        self.title = title
        self.url = url
        self.doi = doi
        self.author = author
        self.date = date
        self.journal = journal
        self.publisher = publisher
        self.pdf = pdf
        self.type = type
        self.abstract = abstract

    @property
    def filename(self) -> str:
        return toname(self.title).strip()


class Article(object):
    def __init__(self, meta: Meta, ajson: list = [], axml: str = ""):
        self.meta = meta
        self.xml = axml
        self.json = ajson

    def to_dict(self) -> dict:
        return {"meta": self.meta.__dict__, "text": self.flatten(self.json)}

    @property
    def filename(self) -> str:
        return self.meta.filename

    def flatten(self, secs, title=""):
        if type(secs) == str:
            return [{"title": title, "text": secs}]
        if type(secs) == list:
            return sum([self.flatten(s, title) for s in secs], [])
        if type(secs) == dict:
            return self.flatten(secs["text"], secs["title"])

    def save(self, loc: str, savexml: bool = False) -> None:
        article_dir = os.path.join(loc, self.filename)
        if not os.path.exists(article_dir):
            os.mkdir(article_dir)
        with open(
            os.path.join(article_dir, "article.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.to_dict(), f, indent=3)
        if savexml and self.xml:
            if type(self.xml) == bytes:
                with open(os.path.join(article_dir, "article.xml"), "wb") as f:
                    f.write(self.xml)
            else:
                with open(
                    os.path.join(article_dir, "article.xml"), "w", encoding="utf-8"
                ) as f:
                    f.write(self.xml)


class Retriever(object):
    def __init__(
        self, journal: str, URL: dict, location: str, savexml: bool = False
    ) -> None:
        super().__init__()
        self.journal = journal
        self.URL = URL
        self.articles = []
        self.sleep = 5
        self.savexml = savexml
        self.location = location
        self.levels = {0: "h2", 1: "h3", 2: "h4", 3: "h5", 4: "p"}
        if not os.path.exists(self.location):
            os.mkdir(self.location)
        self.savedir = os.path.join(self.location, journal)
        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)

    def parse_articles(self, metas: list[Meta]) -> list[Article]:
        articles = []
        available = os.listdir(self.savedir)
        for meta in tqdm(metas, desc="Parsing {}".format(self.journal.capitalize())):
            try:
                if meta.filename not in available:
                    parsed = self.parse_article(meta)
                    time.sleep(self.sleep)
                    parsed.save(self.savedir, self.savexml)
                    articles.append(parsed)
                else:
                    print("\n Already present {}".format(meta.url))
            except:
                print("\n Failed parsing {}".format(meta.url))

        return articles

    def search(self, query, page_range=[0, 1], page_size=50):
        for page in range(page_range[0], page_range[1]):
            metas = self._search(query, page, page_size)
            _ = self.parse_articles(metas)

    def parse_article(self, meta: Meta) -> Article:
        return Article(meta=meta, json=[], xml=[])

    def _search(self, query, page, page_size) -> list[Meta]:
        return []
