from haystack.document_stores import OpenSearchDocumentStore
from haystack.nodes import EmbeddingRetriever, FARMReader, TransformersReader, ElasticsearchRetriever
from haystack.nodes import PreProcessor, BM25Retriever, EmbeddingRetriever, TfidfRetriever
from haystack.pipelines import ExtractiveQAPipeline
import time

paragraph_store = OpenSearchDocumentStore(
    host="127.0.0.1",
    index="paragraph",
    index_type="hnsw",
    embedding_dim=768,
    similarity="cosine",
    return_embedding=True)


def preprocess_data(text_db_to_preprocess):
    """From haystack : function to preprocess data if too large.
    """
    start_time = time.time()

    processor = PreProcessor(
      clean_empty_lines=True,
      clean_whitespace=True,
      clean_header_footer=True,
      split_by="word",
      split_length=200,
      split_respect_sentence_boundary=True,
      split_overlap=0
      )
    docs = processor.process(text_db_to_preprocess)

    return docs


def update_paragraph_embeddings(paragraph_store):
    """Function to create/update vector embeddings for the paragraphs.
    This takes time : better have a handy GPU ...
    """
    paragraph_store.update_embeddings(retriever_update, update_existing_embeddings=False)


def keywords_search(retriever_kw, query, top_k=10, filters={}):
    """Proceed the keywords query based on model given and on the document_store given.
    """
    return retriever_kw.retrieve(query=query, top_k=top_k, filters=filters)


def question_answering(query, pipe=pipe_qa, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}):
    """Perform a question answering through a given pipeline (reader and retriever) on the query given.
    """
    return pipe.run(query=query, params=params)


# Global variables

# Retriever for update
model = 'sentence-transformers/msmarco-distilbert-base-tas-b'
retriever_update = EmbeddingRetriever(document_store=paragraph_store,
                                      embedding_model=model)

# BM25 retriever
retriever_bm25 = BM25Retriever(paragraph_store)

# TFIDF retriever
retriever_tfidf = TfidfRetriever(paragraph_store)

# Embedding retriever
model = "sentence-transformers/msmarco-distilbert-base-tas-b" # In case we don't want the same as for update
retriever_embedding = EmbeddingRetriever(document_store=paragraph_store,
                                         embedding_model=model,
                                         model_format="sentence_transformers")

# Load the reader and retriever model
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
retriever = EmbeddingRetriever(document_store=paragraph_store,
                               embedding_model="sentence-transformers/msmarco-distilbert-base-tas-b",
                               model_format="sentence_transformers")

# Build the pipeline
pipe_qa = ExtractiveQAPipeline(reader, retriever)

