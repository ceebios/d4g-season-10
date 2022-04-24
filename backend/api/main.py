from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import mongo

app = FastAPI()

class SearchOptions(BaseModel):
    # text: list[str]
    keywords: str
    options: dict


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


@app.get("/search/keywords/{text}")
async def simple_search(text):
    docs = mongo.simple_search(text, limit=10)
    # return [text]
    # Now perform some post-processing to get the images from the return docs
    figures_url_list, tables_url_list = mongo.get_images_from_docs(docs)

    return {'figures_list':sum([list(f) for f in figures_url_list],[]), 'tables_list':sum([list(t) for t in tables_url_list],[])}

@app.post("/search/options")
async def full_Search(search:SearchOptions):
    return []