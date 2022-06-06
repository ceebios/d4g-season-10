import re
import xmltodict
import json
import xml.etree.ElementTree as ET
from pprint import pprint

# This code was written by Lucas Le Corvec
def _unique(sequence):
    """Function to remove duplicates while keeping inserterion order.
    """
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def authors_list(value):
    """Function to return main author and other authors through a list of lists.
    """
    if not value:  # Means list is empty
        return '', []
    main_author = value[0][0] + ' ' + value[0][1]
    if len(value) > 1:
        others = [x[0] + ' ' + x[1] for x in value[1:]]
        return main_author, others
    else:
        return main_author, []


def _has_numbers(string):
    """Function to check if string has numeric character.
    """
    return any(char.isdigit() for char in string)

def _numeric_caracter_splitting(string):
    """Function to split figure reference that have a numeric character inside it.
    """
    if 'fig' in string.lower() and _has_numbers(string):
        return re.findall('\d*\D+', string)
    else:
        return string


def figure_ref_detection(text):
    """Function to find figure references in paragraph.
    """
    # Have to take care of figures ref separated by 'and' or/and by ','
    # Plus1 : sometimes '-' is used to reference several figures
    # Plus2 : have to remove any '(' or ')' ',' in figures names after regex

    # Taking care of splitted figure reference that has figure reference inside. Exemple : fig.4B
    # And then flattening the new list
    text_raw = [_numeric_caracter_splitting(x) for x in text.split(' ')]
    text_splitted = []
    for element_1 in text_raw:
        if type(element_1) == list:
            for element_2 in element_1:
                text_splitted.append(element_2)
        else:
            text_splitted.append(element_1)

    figure_ref = []
    for index, element in enumerate(text_splitted):
        if ('fig' in element.lower()) and (
                8 >= len(element) >= 3):  # All figure references "should" validate this condition ==> To verify
            element_to_add = text_splitted[index + 1]  # Get next element as it is the figure reference
            figure_ref.append(element_to_add)
            try:
                text_splitted[index + 2]  # Case 0 : when the figure reference is at the end of paragraph
            except IndexError:
                continue

            if element_to_add.endswith(','):  # Case 1 : element ends with ',' meaning an other figure ref follows
                new_counter = index + 2
                while text_splitted[new_counter].endswith(
                        ','):  # Case 1.1 : several figures references separated by ','
                    figure_ref.append(text_splitted[new_counter])
                    new_counter += 1
                    try:
                        text_splitted[
                            new_counter]  # If it fails it means that the next figure reference is at the end of paragraph
                    except:
                        continue
                if new_counter + 1 == len(text_splitted):  # Case 1.2 : last figure reference is at the end of paragraph
                    figure_ref.append(text_splitted[new_counter])
                    continue
                if text_splitted[new_counter + 1].lower() == 'and':
                    figure_ref.append(
                        text_splitted[new_counter])  # Case 1.3 : get last figure reference, separated by 'and'
                    figure_ref.append(text_splitted[new_counter + 2])
                else:
                    figure_ref.append(
                        text_splitted[new_counter])  # Case 1.4 : get last figure reference, separated by ','

            elif text_splitted[index + 2].lower() == 'and':  # Case 2 : only two figures references, separated by 'and'
                figure_ref.append(text_splitted[index + 3])

            else:  # Case 3 : only one figure reference
                continue  # Element already added

    figure_ref_cleaned_re = [re.sub(r'[,()\'´:"”’.;]', '', x) for x in figure_ref]  # Regex to clean figure references

    # Check if all figure references do have a numeric character and are no longer than 2 characters
    # ==> Maybe double check this rule ...
    for index, element in enumerate(figure_ref_cleaned_re):
        if not _has_numbers(
                element):  # Case 3 : when auhtor doesn't write the figure number for next figure reference. Exemple : fig. 3D, E and F
            figure_ref_cleaned_re[index] = figure_ref_cleaned_re[index - 1][0] + element

    figure_ref_cleaned_len = [x for x in figure_ref_cleaned_re if len(x) <= 3]

    return _unique(figure_ref_cleaned_len)  # In order to remove duplicates


def match_figure_ref(doi, figure_list, dict_figure):
    """Function that matches the figures reference from paragraphs to actual figures in
    dict_figures.
    """
    graphic_ref_list = []
    for element_1 in figure_list:
        # Strip anything that is not digit (including blank spaces)
        figure_ref = re.sub(r'[A-Za-z,()\'´:"”’.; +]', '', element_1)

        for element_2 in dict_figure[doi]:
            # Strip anything that is not digit (including blank spaces)
            graph_ref = re.sub(r'[A-Za-z,()\'´:"”’.; +]', '', element_2)
            # Matching figure_ref from paragraph to figure_ref from figures
            if str(figure_ref) == str(graph_ref):
                graphic_ref_list.append(dict_figure[doi][element_2]['graphic_ref'])

    return graphic_ref_list


## Code by Paul-Henri & Anastasia

def arborescence(filename, counter):
    dic = _file_to_dic(filename)
    d = {}
    _dic_to_keys_dic(dic, d, counter)
    pprint(d)


def _dic_to_keys_dic(dic, keys_dic, counter):
    counter += 1
    keys = dic.keys()
    for key in keys:
        if isinstance(dic[key], dict):
            keys_dic[key] = {}
            nested = dic[key]
            nested_keys = nested.keys()
            _dic_to_keys_dic(dic[key], keys_dic[key], counter)
            counter -= 1
        else:
            keys_dic[key] = counter

def _file_to_dic(f):
    with open(f, "rb") as file:
        document = xmltodict.parse(file)
    json_file_text = json.dumps(document)
    json_file = json.loads(json_file_text)
    dic = json_file['article']
    return dic


class Plos_Parser:
    # This class can parse the following PLOS journals:
    # PLOS One, Genetics, Biology, Computational Biology, Clinical Trials, Neglected Tropical Diseases, Pathogens

    def __init__(self, xml):
        self.xml = xml

    def get_doi(self):
        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the DOI
        doi = root.find(".//*[@pub-id-type='doi']").text
        return doi

    def plos_paragraphs(self):
        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the DOI
        doi = root.find(".//*[@pub-id-type='doi']").text
        print(doi)

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

    def plos_article(self):
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

    def plos_figures(self):

        # Transform the XML file into a parsable object
        tree = ET.parse(self.xml)
        root = tree.getroot()

        # Get the figures URLs
        figure_urls = []
        for r in root.findall(".//fig/object-id"):
            figure_url = "".join(r.itertext())
            figure_urls.append(figure_url)

        # Get the figures IDs
        ids = []
        for l in root.findall(".//fig/label"):
            label = "".join(l.itertext())
            ids.append(label[-1])

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
