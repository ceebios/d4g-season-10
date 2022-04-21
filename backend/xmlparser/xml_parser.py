# region 1.0_LIBRAIRIES

import pubmed_parser as pp # Repo : https://github.com/titipata/pubmed_parser
import glob
import uuid
import os
import logging
import configparser
import datetime
import json

# endregion

# 2.0_FUNCTIONS



# endregion

# 3.0_GLOBAL_VARIABLES

# Configure logger
current_date = datetime.datetime.today().strftime('%Y_%m_%d_%H_%M')
filename = 'xml_parser_log_' + current_date + '.log'
logging.basicConfig(filename=filename, level=logging.INFO)

# Configure configparser
config = configparser.ConfigParser()
config.read('xml_parser_config.ini')

# Get variables from configuration file
path_xml_files = config['DEFAULT']['xmlfilespath']

# Check if db folder exists
path_to_db = os.path.join(os.getcwd(), 'db')
if not os.path.exists(path_to_db):
    os.mkdir(path_to_db)

# endregion

# 4.0_MAIN()

def main():
    path_all = [file for file in glob.glob(os.path.join(path_xml_files, '*.xml'))]
    # Initialize variables and counters
    dict_figure = {}
    dict_text = {}
    error_count = 0
    counter = 0

    if len(path_all) == 0:
        print('Could not get xml files, check xml files path in configuration file !')
        logging.error('Could not get xml files, check xml files path in configuration file !')
        sys.exit()

    # Loop over xml files
    for file in path_all:
        counter += 1
        try:
            # Get main informations
            dict_main_info = pp.parse_pubmed_xml(file)
            doi = dict_main_info['doi']  # Get doi of article
            dict_figure[doi] = {}  # Initialization of new article key
            dict_text[doi] = {}  # Initialization of new article key

            # Get paragraphs
            dict_paragraph = pp.parse_pubmed_paragraph(file, all_paragraph=True)
            for index, element in enumerate(dict_paragraph):
                # Generate a unique key
                paragraph_key = str(uuid.uuid4())
                dict_text[doi][paragraph_key] = {}  # Initialization of paragraph key

                # Add key_value to dict_data
                text = element['text']
                dict_text[doi][paragraph_key]['text'] = text

                # Check if paragraph contains figure references,
                # and remove articles references or supplementary figure reference
                dict_text[doi][paragraph_key]['figure_ref'] = [x for x in element['reference_ids'] if 'c'
                                                               not in x.lower()
                                                               and 'fig' in x.lower()
                                                               and 's' not in x.lower()]

                # Check if paragraph contains table references
                # and remove articles references or supplementary table reference
                dict_text[doi][paragraph_key]['table_ref'] = [x for x in element['reference_ids'] if 'c'
                                                              not in x.lower()
                                                              and 'tbl' in x.lower()
                                                              and 's' not in x.lower()]

            # Get figures
            dict_graph = pp.parse_pubmed_caption(file)
            for element in dict_graph:
                fig_label = element['fig_label']  # Get figure label
                dict_figure[doi][fig_label] = {}  # Initialization of figure label key
                dict_figure[doi][fig_label]['caption'] = element['fig_caption']  # Get figure caption
                # Get figure graphic reference and remove 'v' in it which corresponds to the version
                # of the article but we don't need it
                dict_figure[doi][fig_label]['graphic_ref'] = element['graphic_ref'].replace('v', '')


        except Exception as e:
            error_count += 1
            print('Error while processing file {}'.format(file))
            print('Error : {}\n'.format(e))
            logging.error('Error while processing file {}'.format(file), exc_info=1)


    print('Number of treated files = {}\n'.format(len(path_all)))
    print('Percentage of untreated files = {:.1%}'.format(error_count / len(path_all)))
    logging.info('Percentage of untreated files = {:.1%}'.format(error_count / len(path_all)))

    # Save dicts as json
    with open(os.path.join(path_to_db, 'text_db.json'), 'w') as f1:
        json.dump(dict_text, f1)

    with open(os.path.join(path_to_db, 'figure_db.json'), 'w') as f2:
        json.dump(dict_figure, f2)

if __name__ == '__main__':
    main()

# endregion