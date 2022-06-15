from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
#import mongo
import opensearch
import ml
import time

app = FastAPI()


class Text(BaseModel):
    text: str


class TextWithOptions(BaseModel):
    keywords: str
    option: dict


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

@app.post("/search")
async def search_with_specific_figures_class(text:TextWithOptions):
    results_number = 100

    # Embedding retriever
    docs = opensearch.keywords_search(opensearch.retriever_embedding, query=text.keywords,top_k=results_number, filters={})

    # Now perform some post-processing to get the images from the return docs
    docs_with_figures = opensearch.associate_docs_to_figure(docs, opensearch.figure_store)

    # Filter the documents with specified image class asked
    docs_filtered = opensearch.filter_query(text.option, docs_with_figures)

    # Flatten
    docs_flat = opensearch.flatten_figures(docs_filtered)

    # TODO : in the future we will have to search the database to get the paragraphs links to the figures in order
    #  to do the summarization on all of theses paragraphs
    # Perform summarization on each paragraph returned
    #docs_processed_w_summarization = opensearch.summarize(docs_with_figures)

    return docs_flat

@app.post("/summarize")
async def summarize(text:Text):
    return ml.summarize(text.text)
    
# TODO : finish QA
# @app.get("qa/{text}")
# async def question_answering(text):
#     docs = question_answering(query=text, pipe=opensearch.pipe_qa,
#                               params={"Retriever": {"top_k": 10},
#                                       "Reader": {"top_k": 5}})

# TODO : Make it available to specific users in order to avoid update embedding by any uvser
# @app.post("update")
# async def update_paragraph_embeddings():
#     update_paragraph_embeddings(opensearch.paragraph_store)
