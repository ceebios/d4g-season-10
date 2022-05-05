'''
Prerequisite: https://opensearch.org/docs/latest/opensearch/install/docker/
'''
import hashlib
from haystack.document_stores import OpenSearchDocumentStore
from haystack.schema import Document
import numpy

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
def load_articles()->list[dict]:
    '''
    Assuming each article is a dict containing two fields: meta and text
    'meta' is a dict containing title, abstract, authors, etc.
    'text':list[str] is the list of paragraphs
    ''' 
    return []

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
    paragraph_store.write_documents(
            documents=paragraphs, duplicate_documents="skip", batch_size=5000
        )       


# Function to create/update vector embeddings for the paragraphs
def update_paragraph_embeddings(model:str='sentence-transformers/msmarco-distilbert-base-tas-b'):
    '''
    This takes time!
    Better have a handy GPU ...
    '''
    retriever = EmbeddingRetriever(
        document_store=paragraph_store,
        embedding_model=model,
    )
    paragraph_store.update_embeddings(retriever, update_existing_embeddings=False)


# Homework #1:
def create_paragraph_summaries(paragraphs:list[str])->list[str]:
    '''
    Given a list of paragraphs return a list of summaries
    '''
    return []

# Homeworh #2:
'''
Edit "articles_to_paragraphs" and add paragraph summary to the 'meta' feild in the paragraphs list
'''

# Homework #3:
'''
Create a new index in the database called 'document' (and its associated 'document_store' Haystack object) add put there all articles
'''

# Homework #4:
'''
Implement a keyword search function on the paragraph index using the following tutorial:
https://haystack.deepset.ai/pipeline_nodes/retriever
Please use BM25Retriever.
'''

# Homework #5:
'''
Implement a semantic search function on the paragraph index using the same tutorial:
https://haystack.deepset.ai/pipeline_nodes/retriever
Please use Embedding retriever.
'''

# Homework #6:
'''
Implement a question answering system using the following tutorial:
https://haystack.deepset.ai/pipeline_nodes/reader
You can use FARMReader method.
Bear in mind: the entry point is a list of documents which were retreived with one of the previous two methods.
Question answering on the entire dataset is extremely slow, that is why the number of documents needs to be reduced first with the retriever.
'''

