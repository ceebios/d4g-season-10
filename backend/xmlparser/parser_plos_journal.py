from pprint import pprint
from xml_parser_utils import arborescence, Plos_Parser
import datetime
import logging
import configparser
import os
import glob
import sys
import json

# Parts of the code are copied from xml_parser.py

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

path_xml_files = 'data/biorxiv/biorxiv_test'
path_to_db = 'data/parsed_test_biorxiv'


def main():
    path_all = [file for file in glob.glob(os.path.join(path_xml_files, '*.xml'))]
    journal_type = path_all[0]
    if 'biorxiv' in journal_type:
        journal = 'biorxiv'
    else:
        journal = 'plos'
    counter = 0

    if len(path_all) == 0:
        print('Could not get xml files, check xml files path in configuration file !')
        logging.error('Could not get xml files, check xml files path in configuration file !')
        sys.exit()

    for file in path_all:
        counter += 1
        PLOS = Plos_Parser(file)
        doi = PLOS.get_doi()
        doi = doi.replace('/', '-')
        figs = PLOS.plos_figures()
        article_meta = PLOS.plos_article()
        paragraphs = PLOS.plos_paragraphs()

        # Save dicts as json
        with open(os.path.join(path_to_db, f'{doi}_fig_db.json'), 'w') as f1:
            json.dump(figs, f1)

        with open(os.path.join(path_to_db, f'{doi}_paragraphs_db.json'), 'w') as f2:
            json.dump(paragraphs, f2)

        with open(os.path.join(path_to_db, f'{doi}_meta_db.json'), 'w') as f3:
            json.dump(article_meta, f3)

if __name__ == "__main__":
    main()