import hashlib
from haystack.document_stores import OpenSearchDocumentStore
from haystack.schema import Document
import numpy
import json
import time
from copy import deepcopy
import torch

# Haystack
from haystack.document_stores import OpenSearchDocumentStore
from haystack.nodes import EmbeddingRetriever, FARMReader, TransformersReader, ElasticsearchRetriever
from haystack.nodes import PreProcessor, BM25Retriever, EmbeddingRetriever, TfidfRetriever
from haystack.pipelines import ExtractiveQAPipeline

# Summarization
import transformers

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
    return_embedding=True)

# Create figures database
figure_store = OpenSearchDocumentStore(
    host="127.0.0.1", # TODO : change it for the instance on GCP, the true db
    index="figure",
    index_type="hnsw",
    embedding_dim=768, # TODO : maybe this is going to change
    similarity="cosine", # TODO : same
    return_embedding=True)

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


def associate_docs_to_figure(docs, figure_store):
    """Function that associate, based on docs given, the figures and their caption, from
    the figure_store.
    """
    results = []
    for doc in docs:
        results_dict = {'doi': doc.meta['doi'], 'score': doc.score, 'paragraph_text': doc.content, 'figure_ref': {}}

        # Loop over possible multiple figure references
        for fig in doc.meta['figure_ref']:
            # Get unique fig_id
            fig_id = doc.meta['doi'] + '_' + fig

            # Search the figure database to retrieve the figure
            figures_in_db = figure_store.get_all_documents(filters={"graphic_ref": {"$eq": fig_id}})

            # Check if figure is found in figures database, otherwise next iteration
            if figures_in_db == []:
                continue
            else:
                # TODO : implement figures' url when we have the url of figures
                results_dict['figure_ref'][fig] = {'caption': figures_in_db[0].content, 'url': ''}

        results.append(deepcopy(results_dict))

    return results

##################################################
################## HAYSTACK ######################
##################################################

# Initialize haystack variables that will be needed for the search

# Retriever for update
model = 'sentence-transformers/msmarco-distilbert-base-tas-b'
retriever_update = EmbeddingRetriever(document_store=paragraph_store,
                                      embedding_model=model)

# BM25 retriever
retriever_bm25 = BM25Retriever(paragraph_store)

# TFIDF retriever
retriever_tfidf = TfidfRetriever(paragraph_store)

# Embedding retriever
model = "sentence-transformers/msmarco-distilbert-base-tas-b"  # In case we don't want the same as for update
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


def keywords_search(retriever_kw, query, top_k=10, filters={}):
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
    location_text = 'text_db.json'
    location_figure = 'figure_db.json'
    paragraph_store.delete_all_documents()
    figure_store.delete_all_documents()
    populate_db_paragraphs(location_text, paragraph_store)
    populate_db_figures(location_figure, figure_store)
