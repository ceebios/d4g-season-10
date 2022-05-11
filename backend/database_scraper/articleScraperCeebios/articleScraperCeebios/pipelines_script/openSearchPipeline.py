import hashlib
from typing import List
from haystack.document_stores import OpenSearchDocumentStore
from haystack.schema import Document
import numpy
import json

from itemadapter import ItemAdapter
from base import *




class OpenSearchPipeline:

    hashit = lambda x: hashlib.md5(x.encode()).hexdigest()

    def __init__(self, **param):
        self.param = param

    @classmethod
    def from_crawler(cls, crawler):
        print("heeellllloooo")
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.paragraph_store = OpenSearchDocumentStore(**self.param)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):    
        self.client.close()

    def process_item(self, item, spider):
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
    
    def articles_to_paragraphs(self, articles:List[dict])->List[Document]:
        doc_ids = list(map(self.hashit, [d["meta"]["abstract"] for d in articles]))
        pars = []
        for id, d in zip(doc_ids, articles):
            for j, p in enumerate(d["text"]):
                pars.append({"meta": {"doc": id, "par": j}, "content": p})
        par_ids = list(map(self.hashit, [d["content"] for d in pars]))
        _, ix = numpy.unique(par_ids, return_index=True)
        upars = [pars[i] for i in ix]
        par_ids = [par_ids[i] for i in ix]
        paragraphs = [
            Document(content=d["content"], meta=d["meta"], id=id)
            for d, id in zip(upars, par_ids)
        ]
        paragraph_store.write_documents(
            documents=paragraphs, duplicate_documents="skip", batch_size=5000
        )   
        return paragraphs

    def write_paragraphs(paragraphs:List[Document]):



    
if __name__ == "__main__":
   paragraph_store