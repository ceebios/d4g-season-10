from haystack.nodes import (
    EmbeddingRetriever,
    FARMReader,
    ElasticsearchRetriever,
)
from haystack.document_stores import OpenSearchDocumentStore

paragraph_store = OpenSearchDocumentStore(
    host="127.0.0.1",
    index="paragraph",
    index_type="hnsw",
    embedding_dim=768,
    similarity="cosine",
    return_embedding=True)

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
