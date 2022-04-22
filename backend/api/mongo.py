from pymongo import MongoClient 

client = MongoClient("mongodb://localhost:27017/") 
db = client["Main"] # Assumes database name 'Main'
articles = db["articles"] # Assumes collection name 'articles' in 'Main'


def create_full_text_index():
    '''
    This function shows how to create a full text index directly using the python client
    We need to create a list of all fields of the document we want to index.
    paragraph = 
    {
        'meta':{
            'doi':str
            'para_key':str
            'figure_ref':list[str]
            'table_ref':list[str]
        },
        'text':str
    }

    For nested structures we need to add separately, i.e. /sections/sections/text, etc.
    '''
    indices = []
    indices.append(('text','text'))
    articles.create_index(indices, name='text')    


def simple_search(keywords:str, limit:int=10):
    '''
    Shows to to perform simple full text search and limits answers to 10 enntries by default.
    Entries are sorted by pertinence.
    '''
    docs = []
    search_term = keywords.replace('','') # Do we need to processing of the keywords phrase? See https://www.mongodb.com/basics/full-text-search
    cursor = articles.find({"$text":{"$search":search_term}}, {"score":{"$meta":"textScore"}})
    for doc in cursor.sort([('score', {'$meta': 'textScore'})]).limit(limit):
        doc['_id'] = str(doc['_id'])
        docs.append(doc)
    return docs

def full_search(keywords:str, options:dict):
    return []

def populate_articles(location:str): # location of data
    '''
    Fill in the database
    '''
    return None