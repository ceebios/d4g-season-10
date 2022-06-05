from pprint import pprint
from xml_parser_utils import arborescence, Plos_Parser

if __name__ == "__main__":
    file = 'data/Copie de journal.ppat.0010004.xml'
    counter = 0
    arborescence(file, counter)
    PLOS = Plos_Parser(file)
    article = PLOS.plos_article()
    pprint(article)
    print('---------------')
    figs = PLOS.plos_figures()
    pprint(figs)