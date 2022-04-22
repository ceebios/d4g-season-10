from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import mongo

app = FastAPI()

class SearchOptions(BaseModel):
    # text: list[str]
    keywords: list
    options: dict


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

def get_images_from_docs(docs:list)->list[str]:
    return []

@app.get("/")
async def read_root():
    return {"Ping": "Pong"}


@app.get("/search/keywords/{text}")
async def simple_search(text):
    docs = mongo.simple(text)
    # Now perform some post-processing to get the images from the return docs
    image_url_list = get_images_from_docs(docs)
    return image_url_list

@app.post("/search/options")
async def full_Search(search:SearchOptions):
    assert 1==0, 'Not implemented'    
    return []