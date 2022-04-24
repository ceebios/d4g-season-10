import os
from tqdm import tqdm
import requests
import urllib,shutil
from base import HOME
import os
from bs4 import BeautifulSoup

class Biorxiv():
    def __init__(self, location:str=os.path.join(HOME, 'biorxiv')) -> None:
        self.api = "https://api.biorxiv.org/details/biorxiv/"
        self.biorxiv = "https://www.biorxiv.org/content/10.1101/"
        self.location = location
        if not os.path.exists(HOME):
            os.mkdir(HOME)
        if not os.path.exists(location):
            os.mkdir(location)
        if not os.path.exists(os.path.join(location,'PDF')):
            os.mkdir(os.path.join(location,'PDF'))
        if not os.path.exists(os.path.join(location,'XML')):
            os.mkdir(os.path.join(location,'XML'))

    def get_meta(self, doi:str):
        url = self.api+doi.replace('https://doi.org/','')
        return requests.get(url).json()['collection'][-1]

    def get_xml(self, meta:dict):
        response =  urllib.request.urlopen(meta['jatsxml'])     
        return response.read()

    def get_pdf_url(self, xml):
        soup = BeautifulSoup(xml, "lxml")
        el = soup.find('self-uri',{'content-type':'pdf','c:role':"http://schema.highwire.org/variant/full-text"})
        urlpart = el.get('xlink:href').split('/')[-1].replace('.pdf','')
        return '{}{}.full.pdf'.format(self.biorxiv, urlpart)

    def main(self, dois:list[str]):
        for doi in tqdm(dois):
            title = doi.replace('https://doi.org/','').replace('/','-')
            meta = self.get_meta(doi)
            xml = self.get_xml(meta)
            pdf_url = self.get_pdf_url(xml)
            # Save
            with urllib.request.urlopen(pdf_url) as response, open(os.path.join(self.location,"PDF",title+'.pdf'), 'wb') as f:
                shutil.copyfileobj(response, f)
            f.close()
            with open(os.path.join(self.location,"XML",title+'.xml'), 'wb') as f:
                f.write(xml)
            f.close()



     
        
        