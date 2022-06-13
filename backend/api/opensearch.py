import hashlib
import numpy as np
import glob
import os
import json
import re
import pandas as pd
import math

# Haystack
from haystack.schema import Document
from haystack.document_stores import OpenSearchDocumentStore
from haystack.nodes import EmbeddingRetriever, FARMReader, TransformersReader, ElasticsearchRetriever
from haystack.nodes import PreProcessor, BM25Retriever, EmbeddingRetriever, TfidfRetriever
from haystack.pipelines import ExtractiveQAPipeline
import time
from copy import deepcopy

# DL
import transformers
import torch

##################################################
################# OPENSEARCH #####################
##################################################

# Create connection to OpenSearch DB (in fact directly to an index called 'paragraph' where we'll store all paragraphs)
paragraph_store = OpenSearchDocumentStore(
    host="127.0.0.1", # TODO : change it for the instance on GCP, the true db
    index="paragraph",
    index_type="hnsw",
    embedding_dim=768, # TODO : maybe this is going to change
    similarity="cosine", # TODO : same
    return_embedding=False)

# Create figures database
figure_store = OpenSearchDocumentStore(
    host="127.0.0.1", # TODO : change it for the instance on GCP, the true db
    index="figure",
    index_type="hnsw",
    embedding_dim=768, # TODO : maybe this is going to change
    similarity="cosine", # TODO : same
    return_embedding=False)

# We'll use this to create IDs for the paragrahps in the DB
hashit = lambda x: hashlib.md5(x.encode()).hexdigest()

# Method to load articles
def load_articles(file)->dict:
    # THIS IS UNFINISHED -- DEPENDS ON THE ARTICLE SOURCE


    article = json.load(open(file, "r"))
    meta_dict = {}
    list_metadata = ['doi', 'journal', 'year', 'title', 'authors', 'keywords', 'pmid']
    for metadata in list_metadata:
        if metadata != 'pmid':
            meta_dict[metadata] = article['meta'][metadata]
        else:
            pmid = article['meta'][metadata].split('/')[-2]
            meta_dict[metadata] = pmid




    return

# Method to breakdown articles to paragraphs and return a list of Haystack Documents
def articles_to_paragraphs(articles:list)->list:
    # Create IDs for the documents (so we keep in memory where paragraphs are coming from)
    doc_ids = list(map(hashit, [d["meta"]["abstract"] for d in articles]))

    # Create paragraphs
    # Paragraph is a dict containing 'meta' and 'content'
    # 'meta' contains the doc id the paragraph is coming from as the paragraph number
    # 'content' is the paragraph text
    pars = []
    for id, d in zip(doc_ids, articles):
        for j, p in enumerate(d["text"]):
            pars.append({"meta": {"doc": id, "par": j}, "content": p})
    par_ids = list(map(hashit, [d["content"] for d in pars]))

    # Keep only unique paragraphs
    _, ix = numpy.unique(par_ids, return_index=True)
    upars = [pars[i] for i in ix]
    par_ids = [par_ids[i] for i in ix]

    # Create list of Haystack documents
    paragraphs = [
        Document(content=d["content"], meta=d["meta"], id=id)
        for d, id in zip(upars, par_ids)
    ]
    return paragraphs

def write_paragraphs(paragraphs, index):
    # ASSUMING WE HAVE ALREADY A JSON OF THE FOLLOWING STRUCTURE:
    # {"meta" : {"title": "XXX", "pmid": "11111"},
    #           "fig1" : "concatenated text fig 1", "fig2" : "concatenated text fig 2"}
    paragraph_store.write_documents(
            documents=paragraphs,
            index=index,
            duplicate_documents="skip", batch_size=5000
        )

def populate_db_paragraphs(location:str, index:str): # location of data
    '''
    This function is used to populate the opensearch database with paragraphs.
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
            element_to_add['meta']['figure_ref'] = [x for x in set(value_2['figure_ref'])]

            # Add  content
            element_to_add['content'] = value_2['text']

            # Check if paragraph contains either figure reference or table reference
            if element_to_add['meta']['figure_ref'] != []:
                dict_to_list.append(element_to_add)

    # Insert the prepared articles into the database
    try:
        write_paragraphs(dict_to_list, index)
    except Exception as e:
        return print('An error has occured during the insertion in the database :\n', e)

    return print('Database has been populated with paragraphs')


def populate_db_figures(location:str, index:str): # location of data
    '''
    This function is used to populate the opensearch database with figures.
    '''
    # Read json containing all the figures extracted from xml files
    with open(location, 'r') as f2:
        figure_db = json.load(f2)

    # Map figure_db into list to insert it into opensearch
    dict_to_list = []
    for key_1, value_1 in figure_db.items():
        for key_2, value_2 in value_1.items():
            # Initialize key
            element_to_add = {}

            # Add metadata informations
            element_to_add['meta'] = {}
            element_to_add['meta']['doi'] = key_1
            element_to_add['meta']['figure'] = key_2
            element_to_add['meta']['graphic_ref'] = key_1 + '_' + value_2['graphic_ref'].split('_')[-1]

            # Add  content
            element_to_add['content'] = value_2['caption']

            # Check if figure is not a "supplementary figure" because if so, it won't be referenced
            # in paragraphs (with pubmed parser)
            if 'supplementary' not in element_to_add['meta']['figure'].lower():
                dict_to_list.append(element_to_add)

    # Insert the prepared articles into the database
    try:
        write_paragraphs(dict_to_list, index)
    except Exception as e:
        return print('An error has occured during the insertion in the database :\n', e)

    return print('Database has been populated with figures')


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def populate_db_figures_from_parquet(location: str,
                                     index: str):

    df_db = pd.read_parquet(location, engine='pyarrow')
    df_db_cleaned = df_db.drop(columns=['type', 'content_len', 'content_char_len', 'local_uri', 'img_preprocessed',
                                        'image_embbeddings', 'image_embeddings'])

    # Convert df to dict
    dict_db_cleaned = df_db_cleaned.to_dict(orient='records')

    error_counter = 0
    dict_to_list = []
    for key_1, value_1 in enumerate(dict_db_cleaned):
        try:
            # Initialize key
            element_to_add = {}

            # Add  content
            element_to_add['content'] = value_1['content']

            # Add metadata informations
            element_to_add['meta'] = {'doi': value_1['doi'], 'fig_id': value_1['fig_id'],
                                      'url': value_1['url'], 'full_uri': value_1['full_uri'],
                                      'image_label': value_1['image_label'],
                                      'image_sub_labels': value_1['image_sub_labels']}

            # Check if paragraph contains either figure reference or table reference
            if element_to_add['meta']['fig_id'] != []:
                dict_to_list.append(deepcopy(element_to_add))
        except KeyError as e:
            error_counter += 1
            continue

    print('Number of figures unprocessed = {:.1%} ({} elements)'.format(error_counter / len(dict_db_cleaned),
                                                                        error_counter))

    # Insert the prepared articles into the database
    if len(dict_to_list) >= 10000:  # Can't insert more than 10k articles at once
        n = math.ceil(len(dict_to_list) / 10000)
        splitted = split(dict_to_list, n)
        for splitted_list in splitted:
            try:
                write_paragraphs(splitted_list, index)
            except Exception as e:
                print('An error has occured during the insertion in the database :\n', e)

    return print('Database has been populated with figures')


def populate_db_paragraphs_from_parquet(location: str,
                                        index: str):

    error_counter = 0
    df_db = pd.read_parquet('paragraph_with_txt_embeddings.parquet',
                            engine='pyarrow')
    df_db_cleaned = df_db.drop(columns=['type', 'content_len', 'content_char_len'])

    # TODO : Add empty summary for now but we will have to delete this line !
    df_db_cleaned['paragraph_summary'] = df_db_cleaned.shape[0] * ['']

    # Convert figures_ids from np.array to list
    df_db_cleaned['figures_ids'] = df_db_cleaned['figures_ids'].apply(lambda x: list(x))

    # Convert df to dict
    dict_db_cleaned = df_db_cleaned.to_dict(orient='records')

    dict_to_list = []

    for key_1, value_1 in enumerate(dict_db_cleaned):
        try:
            # Initialize key
            element_to_add = {}

            # Add  content
            element_to_add['content'] = value_1['content']

            # Add embedding
            element_to_add['embedding'] = np.asarray(value_1['content_embeddings'])

            # Add metadata informations
            element_to_add['meta'] = {'doi': value_1['doi'], 'document_id': value_1['document_id'],
                                      'figures_ids': value_1['figures_ids'],
                                      'paragraph_summary': value_1['paragraph_summary']}

            # Check if paragraph contains either figure reference or table reference
            if element_to_add['meta']['figures_ids'] != []:
                dict_to_list.append(deepcopy(element_to_add))
        except KeyError as e:
            error_counter += 1
            continue

    print('Number of paragraphs unprocessed = {:.1%} ({} elements)'.format(error_counter / len(dict_db_cleaned),
                                                                           error_counter))

    # Insert the prepared articles into the database
    if len(dict_to_list) >= 10000:  # Can't insert more than 10k articles at once
        n = math.ceil(len(dict_to_list) / 10000)
        splitted = split(dict_to_list, n)
        for splitted_list in splitted:
            try:
                write_paragraphs(splitted_list, index)
            except Exception as e:
                print('An error has occured during the insertion in the database :\n', e)

    return print('Database has been populated with figures')


def associate_docs_to_figure(docs, figure_store):
    """Function that associate, based on docs given, the figures and their caption, from
    the figure_store.
    """
    results = []
    for doc in docs:
        results_dict = {'doi': doc.meta['doi'], 'score': doc.score, 'document_id': doc.meta['document_id'],
                        'paragraph_text': doc.content, 'figures_ids': {},
                        'paragraph_summary': doc.meta['paragraph_summary']}

        # Loop over possible multiple figure references
        for fig in doc.meta['figures_ids']:
            # Get unique fig_id
            fig_id = doc.meta['doi'] + '_' + re.sub('[^0-9]', '', fig)  # In order to remove non numeric character

            # Search the figure database to retrieve the figure
            figures_in_db = figure_store.get_all_documents(filters={
                "fig_id": {"$eq": fig_id}
            })

            # Check if figure is found in figures database
            if figures_in_db == []:
                continue
            else:
                results_dict['figures_ids'][fig] = {'caption': figures_in_db[0].content,
                                                   'url': figures_in_db[0].meta['url'],
                                                   'image_label': figures_in_db[0].meta['image_label']
                                                  }

        results.append(deepcopy(results_dict))

    return results


def filter_query(filter_dict, results):
    """Function that filters results based on image label asked by user
    """
    # Mapping between frontend and backend
    filters = {'drawing_simu': filter_dict['DrawingSimu'],
               'map': filter_dict['Map'],
               'molecules': filter_dict['Molecules'],
               'photo_macro': filter_dict['PhotoMacro'],
               'photo_micro': filter_dict['PhotoMicro'],
               'plots': filter_dict['Plots'],
               'table': filter_dict['Table']
               }

    # Build the filter
    filters = [key for key, value in filters.items() if value == 'true']

    # Filtering out all image_labels not requested
    results_filtered = []
    for item in results:
        results_copy = deepcopy(item)
        results_copy['figures_ids'] = {k: v for k, v in item['figures_ids'].items()
                                       if v['image_label'] in filters}
        if results_copy['figures_ids'] != {}:
            results_filtered.append(deepcopy(results_copy))

    return results_filtered

##################################################
################## HAYSTACK ######################
##################################################

# Initialize haystack variables that will be needed for the search

# Retriever for update
model = 'pritamdeka/S-PubMedBert-MS-MARCO-SCIFACT'
retriever_update = EmbeddingRetriever(document_store=paragraph_store,
                                      embedding_model=model)

# BM25 retriever
retriever_bm25 = BM25Retriever(paragraph_store)

# TFIDF retriever
retriever_tfidf = TfidfRetriever(paragraph_store)

# Embedding retriever
model = 'pritamdeka/S-PubMedBert-MS-MARCO-SCIFACT'  # In case we don't want the same as for update
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


def keywords_search(retriever_kw, query, top_k=100, filters={}):
    """Proceed the keywords query based on model given and on the document_store given.
    """
    return retriever_kw.retrieve(query=query, top_k=top_k, filters=filters)


def question_answering(query, pipe, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}):
    """Perform a question answering through a given pipeline (reader and retriever) on the query given.
    """
    return pipe.run(query=query, params=params)


##################################################
############### SUMMARIZATION ####################
##################################################

summarization_model_name = "facebook/bart-large-cnn"
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = transformers.BartTokenizer.from_pretrained(summarization_model_name)
model = transformers.BartForConditionalGeneration.from_pretrained(summarization_model_name).to(device)


def summarize(docs):
    """Function that takes docs_processed with content, meta, and associate figure and return the same docs
    with an new entry that is the paragraph summarized by the model (bartlargecnn here)
    """
    src_text = [doc['paragraph_text'] for doc in docs]
    batch = tokenizer(src_text, truncation=True, padding="longest", return_tensors="pt").to(device)
    translated = model.generate(**batch)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)

    return [dict(item, **{'summarized_paragraph': tgt_text[index]}) for index, item in enumerate(docs)]


if __name__=='__main__':
    # TODO : Implement here the scrapping into parsing into db ingestion ?

    # Construct initial database
    location_text = 'processed_database_parquet_ceebios_plos_database_parquet_20220613.parquet'
    location_figure = 'paragraph_with_txt_embeddings.parquet'
    paragraph_store.delete_all_documents()
    figure_store.delete_all_documents()
    populate_db_paragraphs_from_parquet(location_text, 'paragraph')
    populate_db_figures_from_parquet(location_figure, 'figure')
