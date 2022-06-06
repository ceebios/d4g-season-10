'''
Prerequisite: https://opensearch.org/docs/latest/opensearch/install/docker/
'''
import hashlib
from haystack.document_stores import OpenSearchDocumentStore
from haystack.schema import Document
import numpy
import json


# Create connection to OpenSearch DB (in fact directly to an index called 'paragraph' where we'll store all paragraphs)
paragraph_store = OpenSearchDocumentStore(
    host="127.0.0.1",
    index="paragraph",
    index_type="hnsw",
    embedding_dim=768,
    similarity="cosine",
    return_embedding=True)

# We'll use this to create IDs for the paragrahps in the DB
hashit = lambda x: hashlib.md5(x.encode()).hexdigest()

# Method to load articles
def load_articles(file)->dict:
    # THIS IS UNFINISHED -- DEPENDS ON THE ARTICLE SOURCE


    article = json.load(open(file, "r"))
    meta_dict = {}
    list_metadata = ['doi', 'journal', 'year', 'title', 'authors', 'keywords', 'pmid']
    for metadata in list_metadata:
        if metadata != 'pmid':
            meta_dict[metadata] = article['meta'][metadata]
        else:
            pmid = article['meta'][metadata].split('/')[-2]
            meta_dict[metadata] = pmid

    return

# Method to breakdown articles to paragraphs and return a list of Haystack Documents
def articles_to_paragraphs(articles:list[dict])->list[Document]:
    # Create IDs for the documents (so we keep in memory where paragraphgs are coming from)
    doc_ids = list(map(hashit, [d["meta"]["abstract"] for d in articles]))

    # Create paragraphs
    # Paragraph is a dict containing 'meta' and 'content'
    # 'meta' contains the doc id the paragraph is coming from as the paragraph number
    # 'content' is the paragraph text
    pars = []
    for id, d in zip(doc_ids, articles):
        for j, p in enumerate(d["text"]):
            pars.append({"meta": {"doc": id, "par": j}, "content": p})
    par_ids = list(map(hashit, [d["content"] for d in pars]))

    # Keep only unique paragraphs
    _, ix = numpy.unique(par_ids, return_index=True)
    upars = [pars[i] for i in ix]
    par_ids = [par_ids[i] for i in ix]

    # Create list of Haystack documents
    paragraphs = [
        Document(content=d["content"], meta=d["meta"], id=id)
        for d, id in zip(upars, par_ids)
    ]
    return paragraphs

def write_paragraphs(paragraphs:list[Document]):
    # ASSUMING WE HAVE ALREADY A JSON OF THE FOLLOWING STRUCTURE:
    # {"meta" : {"title": "XXX", "pmid": "11111"},
    #           "fig1" : "concatenated text fig 1", "fig2" : "concatenated text fig 2"}
    paragraph_store.write_documents(
            documents=paragraphs, duplicate_documents="skip", batch_size=5000
        )