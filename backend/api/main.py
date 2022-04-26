from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import mongo
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


@app.get("/search/{text}")
async def simple_search(text):
    docs = mongo.simple_search(text, limit=10)
    # return [text]
    # Now perform some post-processing to get the images from the return docs
    figures = mongo.get_images_from_docs(docs)

    return [{'figure':k,'caption':v['caption'],'paragraph':v['paragraph']} for k,v in figures.items()]

@app.post("/summarize")
async def summarize(text:Text):
    return ml.summarize(text.text)