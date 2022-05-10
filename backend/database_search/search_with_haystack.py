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
    return_embedding=True,
)


from haystack.nodes import (
    EmbeddingRetriever,
    FARMReader,
    ElasticsearchRetriever,
)

# We'll use this to create IDs for the paragrahps in the DB
hashit = lambda x: hashlib.md5(x.encode()).hexdigest()

# Method to load articles
def load_articles(list_files)->list[dict]:
    '''
    Assuming each article is a dict containing two fields: meta and text
    'meta' is a dict containing title, abstract, authors, etc.
    'text':list[str] is the list of paragraphs
    '''

    for file in list_files:
        article = json.load(open(file, "r"))

    return []