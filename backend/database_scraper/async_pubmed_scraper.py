from metapub import PubMedFetcher
import requests
import pubmed_parser as pp
from aiohttp import ClientSession
import asyncio
from joblib import Parallel, delayed
import tqdm



async def get_response(pmid, session):
    '''
    get_response: Asyncio function to get the response of the URL using ClientSession
    --> Returns an html_body that can be used for BeautifulSoup
    '''

    PMC_BASE_URL = 'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml'
    url = PMC_BASE_URL + '/' + pmid + '/unicode'

    async with session.get(url) as response:
        if response.status == 200:
            html_body = await response.text()
        else:
            html_body = ''
        return html_body


async def get_response_with_semaphore(pmid, session, sem):
    '''
    Use a Semaphore to limit the number of simultaneous connections to the website
    get_response_with_semaphore: Asyncio function to get the response of the URL using ClientSession
    --> Returns an html_body that can be used for BeautifulSoup
    '''

    PMC_BASE_URL = 'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml'
    url = PMC_BASE_URL + '/' + pmid + '/unicode'
    async with sem:
        async with session.get(url) as response:
            if response.status == 200:
                html_body = await response.text()
            else:
                html_body = ''
            return html_body

async def request_list_pmids(pmids_list):
    '''
    request_list_pmids: Using the get_response_with_semaphore asyncio function and a ClientSession,
    get responses for a list of pmids, here the limit is 40 requests simultaneously
    --> Returns a list of responses that can be used for BeautifulSoup
    '''

    tasks = []
    sem = asyncio.Semaphore(40)
    async with ClientSession() as session:
        for pmid in pmids_list:
            tasks.append(asyncio.create_task(get_response_with_semaphore(pmid, session, sem)))
        list_of_responses_from_pmids = await asyncio.gather(*tasks)
        return list_of_responses_from_pmids


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
    return unique_list


def fetch_xml(x):
    '''
    This function checks one by one the articles by their PMID and when available downloads the xml from Open PMC and saves it.
    :param pmid_number: (str)
    :return: None
    '''

    for y in range(x, x + 20, 5):
        pmid_sublist = pmid_list[y:y + 5]
        # Do this for Windows machines
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        results = asyncio.run(request_list_pmids(pmid_sublist))

        for i, result in enumerate(results):
            pmid_number = pmid_sublist[i]
            PMC_BASE_URL = 'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml'

            url = PMC_BASE_URL + '/' + pmid_number + '/unicode'
            if result != '':
                print(result)
                article_info = pp.parse_xml_web(url)
                # The DOI is needed in order to name xml files in a correct way
                doi = article_info['doi'].replace('/', '-')
                with open(f'xml_data/{doi}.xml', 'wb') as file:
                    file.write(result.content)


#
#     print(link_to_article)
#     r = requests.get(link_to_article)
#     if r:
#         article_info = pp.parse_xml_web(link_to_article)
#         # The DOI is needed in order to name xml files in a correct way
#         doi = article_info['doi'].replace('/', '-')
#         with open(f'xml_data/{doi}.xml', 'wb') as file:
#             file.write(r.content)
#
#
# def run(keyword):
#     pmids = fetch_list_pmid(keyword)
#     for pmid in pmids:
#         fetch_xml(pmid)


if __name__ == "__main__":
    keyword = 'Ty1 integrase'
    # run(keyword)
    pmid_list = fetch_list_pmid(keyword)
    Parallel(n_jobs=2)(delayed(fetch_xml)(i) for i in tqdm.tqdm(range(0, 100)))
