from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from ..database_scraper import fetch_list_pmid, fetch_xml, run_xml_download

print(run_xml_download())
fetch_xml(2356)
print('something')
run_xml_download()



