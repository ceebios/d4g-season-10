import pubmed_parser as pp
import glob
from xml_parser_utils import unique, authors_list, has_numbers, numeric_caracter_splitting, figure_ref_detection, match_figure_ref
from pprint import pprint
import json

path = 'data/10.1101-2020.06.03.131375.xml'
path_all = [file for file in glob.glob('data/*.xml')]

# test = [['Villa', 'Paolo', 'a1'],
#   ['Bolpagni', 'Rossano', 'a1'],
#   ['Bolpagni', 'Rossano', 'a2'],
#   ['Pinardi', 'Monica', 'a1'],
#   ['Tóth', 'Viktor R.', 'a3']]
#
# print(authors_list(test))

dict_main_info = pp.parse_pubmed_xml(path)
print(dict_main_info)

dict_paragraph = pp.parse_pubmed_paragraph(path, all_paragraph=True)
pprint(dict_paragraph)

dict_graph = pp.parse_pubmed_caption(path)
pprint(dict_graph)

# # Parsing tables
# dict_table = pp.parse_pubmed_table(path, return_xml=False)
# print(dict_table)

# articles_title = []
# for file in path_all:
#     dict_main_info = pp.parse_pubmed_xml(file)
#     #print(dict_main_infos['doi'], dict_main_infos['full_title'],'\n')
#     articles_title.append(dict_main_info['full_title'])
#     dict_table = pp.parse_pubmed_table(path, return_xml=False)
#     print(dict_table)


# Create a dict that contains information about every figure: its caption and its mentions in the text

list_fig = []
for fig in dict_graph:
    list_fig.append(fig['fig_id'])
list_fig = list(set(list_fig))
print(list_fig)

fig_legends = {}
for fig in dict_graph:
    num = fig['fig_id']
    legend = fig['fig_caption']
    fig_legends[num] = legend

pprint(fig_legends)
print('-------------------------')
fig_paragraph = {}
for paragraph in dict_paragraph:
    for ref in paragraph['reference_ids']:
        if ref in list_fig:
            try:
                pre_existing_text = fig_paragraph[ref]
                updated_text = pre_existing_text + ' ' + paragraph['text']
                fig_paragraph[ref] = updated_text
            except:
                fig_paragraph[ref] = paragraph['text']

pprint(fig_paragraph)
json.dump(fig_paragraph, open('data/test_json/test.json', "w"))
