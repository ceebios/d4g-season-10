import configparser
config = configparser.ConfigParser()
config['DEFAULT'] = {'xmlFilesPath' :
                         '/Users/mac/Desktop/Projects/6.0_DataForGood/2.0_Ceebios/d4g-season-10/xml_parser/xml'}

with open('xml_parser_config.ini', 'w') as configfile:
  config.write(configfile)