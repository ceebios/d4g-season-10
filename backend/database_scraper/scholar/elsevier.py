import requests
import json
import os
from .base import Article, Meta, Retriever, HOME
import re
from tqdm import tqdm
import time
from xml.etree import ElementTree as ET
from . import keys
import re

URL = {
    "search": """https://api.elsevier.com/content/search/sciencedirect""",
    "article": "https://api.elsevier.com/content/article/doi/{}?view=FULL&apiKey={}",
}


def totext(xml):
    text = " ".join([t for t in xml.itertext()]).replace("\n", " ")
    return re.sub(" +", " ", text).strip()


def xml_to_text(xml):
    if type(xml) == list:
        return [xml_to_text(x) for x in xml]
    if "full-text-retrieval-response" in xml.tag:
        sections = xml.findall(".//{*}sections")
        if len(sections) > 0:
            return [xml_to_text(sec) for sec in sections]
        full = totext(xml.find(".//{*}rawtext"))
        core = xml.find(".//{*}coredata")
        title = core.find("{*}title").text
        abstract = totext(xml.find(".//{*}abstract"))
        dic = [{"title": "title", "text": title}]
        dic += [{"title": "abstract", "text": abstract}]
        dic += [{"title": "fulltext", "text": full}]
        return dic
    if "sections" in xml.tag:
        return [xml_to_text(sec) for sec in xml]
    if "section" in xml.tag:
        children = [sec for sec in xml]
        if "label" in children[0].tag:
            children = children[1:]
        assert "section-title" in children[0].tag, "Exptected Section Title"
        dic = {"title": children[0].text, "text": []}
        for child in children[1:]:
            if "para" in child.tag:
                dic["text"].append(totext(child))
            if "section" in child.tag:
                dic["text"].append(xml_to_text(child))
        return dic
    if "para" in xml.tag:
        return totext(xml)


class Elsevier(Retriever):
    def __init__(self, location=HOME) -> None:
        super().__init__(journal="elsevier", location=location, URL=URL)
        self.sleep = 5

    def _search(self, query, page, page_size) -> list[Meta]:
        headers = {"X-ELS-APIKey": keys.elsevier_search, "Accept": "application/json"}
        payload = {
            "qs": query,
            "filters": {"openAccess": True},
            "display": {"offset": page * page_size, "show": page_size},
        }

        res = requests.put(URL["search"], data=json.dumps(payload), headers=headers)
        res = res.json().get("results", [])

        metas = [
            Meta(
                title=r["title"],
                doi=r["doi"],
                url=URL["article"].format(r["doi"], keys.elsevier_article),
            )
            for r in res
        ]
        return metas

    def get_meta(self, xml) -> Meta:
        core = xml.find(".//{*}coredata")
        authors = [a.text for a in core.findall("{*}creator")]
        doi = core.find("{*}doi").text
        title = core.find("{*}title").text
        date = core.find("{*}coverDate").text
        journal = core.find("{*}publicationName").text
        publisher = core.find("{*}publisher").text
        link = core.findall("{*}link")
        link = [l.get("href") for l in link if "api.elsevier" not in l.get("href")][0]
        pdf = link + "/pdfft"
        abstract = re.sub(" +", " ", core.find("{*}description").text.replace("\n", ""))
        dtype = (
            xml.find(".//{*}document-type").text
            + "-"
            + xml.find(".//{*}document-subtype").text
        )
        return Meta(
            author=authors,
            doi=doi,
            url=link,
            pdf=pdf,
            date=date,
            journal=journal,
            publisher=publisher,
            title=title,
            abstract=abstract,
            type=dtype,
        )

    def parse_article(self, meta: Meta) -> Article:
        res = requests.get(meta.url)
        xml = ET.XML(res.text)
        meta = self.get_meta(xml)
        return Article(meta=meta, ajson=xml_to_text(xml), axml=res.text)
