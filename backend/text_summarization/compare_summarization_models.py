from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
import sys
sys.path.append("C:\\Users\\headl\\Documents\\github projects\\ceebios\\d4g-season-10\\backend\\database_scraper")
from pubmed_scraper import fetch_list_pmid, fetch_xml, run_xml_download

print(run_xml_download())
fetch_xml(2356)
print('something')
run_xml_download()



