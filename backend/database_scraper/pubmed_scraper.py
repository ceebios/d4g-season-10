from metapub import PubMedFetcher
import os


def fetch_list_pmid(keyword):
    pubmed_fetcher = PubMedFetcher()

    pmids_to_download = None
    retry = 0

    while pmids_to_download is None and retry < 5:
        try:
            pmids_to_download = pubmed_fetcher.pmids_for_query(keyword, retmax=1000000)
        except:
            retry += 1
            pass

    list_of_pmids = []
    list_of_pmids.append(pmids_to_download)
    unique_list = list(set([j for i in list_of_pmids for j in i]))
    return unique_list

def fetch_xml():
    PMC_BASE_URL = 'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml'
    path_to_download = os.path.join(PMC_BASE_URL, pmid_number, 'unicode')

pmids = fetch_list_pmid('Ty1 integrase')
print(pmids)


