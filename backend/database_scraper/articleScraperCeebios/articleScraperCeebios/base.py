import hashlib
from haystack.document_stores import OpenSearchDocumentStore

import numpy
import json

paragraph_store = OpenSearchDocumentStore(
    host="127.0.0.1",
    index="paragraph",
    index_type="hnsw",
    embedding_dim=768,
    similarity="cosine",
    return_embedding=True,
)