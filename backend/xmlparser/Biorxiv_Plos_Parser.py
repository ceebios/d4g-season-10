import xml.etree.ElementTree as ET
from xml_parser_utils import *


class Biorxiv_Plos_Parser:
    # This class can parse the following PLOS journals:
    # PLOS One, Genetics, Biology, Computational Biology, Clinical Trials, Neglected Tropical Diseases, Pathogens

    def __init__(self, xml, journal_type):
        self.xml = xml
        self.journal_type = journal_type

    def get_doi(self):
        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the DOI
        doi = root.find(".//*[@pub-id-type='doi']").text
        return doi

    def get_paragraphs(self):
        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the DOI
        doi = root.find(".//*[@pub-id-type='doi']").text

        # Get the paragraphs and their associated figures
        ## Lists of paragraphs and figures in the body + list of hashes
        figures = []
        hashes = []
        p = []

        ## Select all the paragraphs in the body with xpath (sec)
        e = root.findall(".//sec/p")

        ## Extract the paragraphs and figures
        for i in e:
            paragraph = "".join(i.itertext())
            p.append(paragraph)
            figures.append(figure_ref_detection(paragraph))
            hashes.append(hash(paragraph + doi))

        # Build the paragraph dictionary
        paragraphs = []

        for doc_id, paragraph, figure_list, id_ in zip(hashes, p, figures, hashes):
            dic = {}
            dic['id'] = id_
            dic['content'] = paragraph.replace('\t', '').replace('\n', '')

            meta_dic = {}
            meta_dic['document_id'] = doc_id
            meta_dic['figures_ids'] = figure_list
            meta_dic['type'] = 'paragraph'

            dic['meta'] = meta_dic
            paragraphs.append(dic)

        return paragraphs

    def get_article(self):
        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the DOI
        doi = root.find(".//*[@pub-id-type='doi']").text

        # Get the Abstract
        abstract = []
        for r in root.findall(".//front/article-meta/abstract"):
            abstract_paragraph = "".join(r.itertext()).replace('\t', '').replace('\n', '')
            abstract.append(abstract_paragraph)

        abstract = ''.join(abstract)

        # Get the Title
        title = root.find(".//article-title").text

        # Get the Authors
        authors = []
        for a in root.findall(".//*[@contrib-type='author']/name/surname"):
            author = "".join(a.itertext())
            authors.append(author)

        # Get the journal
        journal = root.find(".//journal-title").text

        # Build the articles dictionary
        article = {}
        article['id'] = hash(doi + abstract)
        article['content'] = abstract

        meta_article = {}
        meta_article['title'] = title
        meta_article['authors'] = authors
        meta_article['journal'] = journal
        meta_article['doi'] = doi

        article['meta'] = meta_article

        return article

    def get_figures(self):

        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the figures URLs
        figure_urls = []
        for r in root.findall(".//fig/object-id"):
            figure_url = "".join(r.itertext())
            figure_urls.append(figure_url)
            if self.journal_type == 'biorxiv':
                figure_urls = [f for f in figure_urls if 'biorxiv' in f]

        # Get the figures IDs
        ids = []
        for l in root.findall(".//fig/label"):
            label = "".join(l.itertext())
            if self.journal_type == 'plos':
                ids.append(label[-1])
            else:
                ids.append(label[-2])

        # Create a string of figure title + its caption. It sometimes can happen that the title or the caption
        # are not present. It will be filled with "Not available" text.
        captions = []
        for fig in root.findall(".//fig"):
            if fig.findall('caption/p') != []:
                c = fig.findall('caption/p')[0]
                caption = "".join(c.itertext()).replace('\t', '').replace('\n', '')
            else:
                caption = 'Caption not found'

            if fig.findall('caption/title') != []:
                t = fig.findall('caption/title')[0]
                title = "".join(t.itertext()).replace('\t', '').replace('\n', '')
            else:
                title = "Title not found"

            captions.append(title + '; ' + caption)

        # Build the figures dictionary
        figures = []
        for url, caption, id_ in zip(figure_urls, captions, ids):
            dic = {}
            dic['id'] = id_
            dic['content'] = caption

            meta_dic = {}
            meta_dic['url'] = url
            meta_dic['type'] = 'figure'

            dic['meta'] = meta_dic
            figures.append(dic)

        return figures
