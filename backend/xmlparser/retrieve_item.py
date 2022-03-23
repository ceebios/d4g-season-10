import os
import lxml 
from lxml import etree
import xml.dom.minidom
import bs4
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def _extract_all_paragraph(soup):
    paragraph = []
    for p in soup.find_all('p'):
        paragraph.append(p.text)
    tags = soup.find_all('a')
    titles = soup.h2
    images = soup.find_all("div")
    print("images")
    print(images)
    return paragraph, tags, titles
def main():
    path_data_xml = '/Users/karinepetrus/Desktop/projectDataForGood/datasets/D4G-season-10/XML' 
    list_xml = os.listdir(path_data_xml)
    for xml_file in list_xml[:1]:
        print(xml_file)
        with open(path_data_xml + "/" +xml_file) as fp:
            soup = BeautifulSoup(fp,"lxml")
        paragraph, tags, titles = _extract_all_paragraph(soup)
        print(paragraph[:10])
        print(tags)
        print(titles)
        doc = xml.dom.minidom.parse(path_data_xml + "/" +xml_file)
        print(doc.nodeName)

if __name__ == "__main__":
    main()
