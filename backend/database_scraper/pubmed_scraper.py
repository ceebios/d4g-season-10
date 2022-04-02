from metapub import PubMedFetcher
import requests
import pubmed_parser as pp
import tqdm
from joblib import Parallel, delayed

def fetch_list_pmid(keyword):
    '''
    This function will fetch a list of PMIDs based on a keyword query (considered as EXACT MATCH)
    Not all of these articles will be available in the Open PMC dataset
    :param keyword: (str) the keyword to search for
    :return: (lst) list of the PMIDs found for that keyword
    '''

    fetcher = PubMedFetcher()
    pmids_to_download = None
    retry = 0

    while pmids_to_download is None and retry < 5:
        try:
            pmids_to_download = fetcher.pmids_for_query(keyword, retmax=1000000)
        except:
            retry += 1
            pass

    unique_list = list(set(pmids_to_download))
    print(f'Done retrieving the list of PMIDs for the keyword {keyword}!')
    return unique_list


def fetch_xml(pmid_number):
    '''
    This function checks one by one the articles by their PMID and when available downloads the xml from Open PMC and saves it.
    :param pmid_number: (str)
    :return: None
    '''
    # this is the base link to the PMC API
    PMC_BASE_URL = 'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml'
    link_to_article = PMC_BASE_URL + '/' + pmid_number + '/unicode'
    r = requests.get(link_to_article)

    if r:
        article_info = pp.parse_xml_web(link_to_article)
        # The DOI is needed in order to name xml files in a correct way
        doi = article_info['doi'].replace('/', '-')
        with open(f'xml_data/{doi}.xml', 'wb') as file:
            file.write(r.content)


def run(keyword):
    pmids = fetch_list_pmid(keyword)
    print(f'Starting downloading articles for the keyword {keyword}')
    for pmid in tqdm.tqdm(pmids):
        fetch_xml(pmid)

def run_parallel(keyword):
    pmids = fetch_list_pmid(keyword)

    def fetch_xml_by_batch(i):
        pmids_truncated = pmids[i:i+30]
        for pmid in pmids_truncated:
            fetch_xml(pmid)


    Parallel(n_jobs=5)(delayed(fetch_xml_by_batch)(i) for i in tqdm.tqdm(range(0, len(pmids), 30)))

if __name__ == "__main__":
    keyword = 'Ty1 integrase'
    run_parallel(keyword)
