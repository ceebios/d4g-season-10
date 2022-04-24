from pymongo import MongoClient
import pymongo
import json

client = MongoClient("mongodb://localhost:27017/") 
db = client["Main"] # Assumes database name 'Main'
articles = db["articles"] # Assumes collection name 'articles' in 'Main'


def create_full_text_index(articles:pymongo.collection.Collection):
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
    Shows to to perform simple full text search and limits answers to 10 entries by default.
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

def populate_db(articles:pymongo.collection.Collection, location:str): # location of data
    '''
    This function is used to populate the mongodb database with articles.
    '''
    # Read json containing all the paragraphs extracted from xml files
    with open(location, 'r') as f1:
        text_db = json.load(f1)

    # Map text_db into list to insert it into mongodb
    dict_to_list = []
    for key_1, value_1 in text_db.items():
        for key_2, value_2 in value_1.items():
            # Initialize key
            element_to_add = {}

            # Add metadata informations
            element_to_add['meta'] = {}
            element_to_add['meta']['doi'] = key_1
            element_to_add['meta']['paragraph_key'] = key_2
            element_to_add['meta']['figure_ref'] = value_2['figure_ref']
            element_to_add['meta']['table_ref'] = value_2['table_ref']

            # Add  content
            element_to_add['text'] = value_2['text']

            # Check if paragraph contains either figure reference or table reference
            if element_to_add['meta']['figure_ref'] != [] or \
                    element_to_add['meta']['table_ref'] != []:
                dict_to_list.append(element_to_add)

    # Insert the prepared articles into the database
    try:
        inserted = articles.insert_many(dict_to_list)
    except Exception as e:
        return print('An error has occured during the insertion in the database :\n', e)

    return print('Database has been populated')

def get_images_from_docs(docs:list):#->list[str]:
    '''
    This functions purpose is, based on the figure_ref in the docs returned,
    to match the corresponding figures and tables.
    '''
    figures_list_global, tables_list_global = [], []
    for doc in docs:
        doi = doc['meta']['doi']
        figure_ref_list = doc['meta']['figure_ref']
        table_ref_list = doc['meta']['table_ref']

        # Check if list is not empty
        if len(figure_ref_list) > 0:
            # The key associate to the figure is doi_figX
            figures_list_doc = [str(doi + '_' + x) for x in doc['meta']['figure_ref']]

            # Remove the duplicates and add it to the global list
            figures_list_global.append(set(figures_list_doc))

        if len(table_ref_list) > 0:
            tables_list_doc = [str(doi + '_' + x) for x in doc['meta']['table_ref'] if doc['meta']['table_ref'] != []]
            tables_list_global.append(set(tables_list_doc))

    return figures_list_global, tables_list_global

if __name__=='__main__':
    location = 'text_db.json'
    populate_db(articles, location)
