from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
#import mongo
import opensearch
import ml

app = FastAPI()

class Text(BaseModel):
    text: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

@app.get("/")
async def read_root():
    return {"Ping": "Pong"}


# @app.get("/search/{text}")
# async def simple_search(text):
#     docs = mongo.simple_search(text, limit=10)
#     # return [text]
#     # Now perform some post-processing to get the images from the return docs
#     figures = mongo.get_images_from_docs(docs)
#
#     return [{'figure':k,'caption':v['caption'],'paragraph':v['paragraph']} for k,v in figures.items()]

# TODO : change it in order to work with "new summarization" pipeline
#  or compute it before and then implement it in each paragraph (in meta)
@app.post("/summarize")
async def summarize(text:Text):
    return ml.summarize(text.text)

@app.get("/search/{text}")
async def simple_search(text):
    # TODO : dans un premier temps on considère la summarization que sur le
    #  paragraphe qui est ressorti par haystack

    # BM25 retriever
    docs = opensearch.keywords_search(opensearch.retriever_bm25, query=text, top_k=10, filters={})

    # TFIDF retriever
    # docs = opensearch.keywords_search(opensearch.retriever_tfidf, query=text, top_k=10, filters={})

    # Enbedding retriever
    # docs = opensearch.keywords_search(opensearch.retriever_embedding, query=text, top_k=10, filters={})

    # Now perform some post-processing to get the images from the return docs
    docs_with_figures = opensearch.associate_docs_to_figure(docs, opensearch.figure_store)

    # TODO : maybe change the structure here, depends on what is needed for the frontend
    return docs_with_figures

# TODO : finish QA
@app.get("qa/{text}")
async def question_answering(text):
    docs = question_answering(query=text, pipe=opensearch.pipe_qa,
                              params={"Retriever": {"top_k": 10},
                                      "Reader": {"top_k": 5}})

# TODO : try this with GPU, and make it available to specific users ?
@app.post("update")
async def update_paragraph_embeddings():
    update_paragraph_embeddings(opensearch.paragraph_store)
