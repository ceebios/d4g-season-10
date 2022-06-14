import gdown

url = 'https://drive.google.com/uc?id=1dZ4Ob9BGKCEmIziyCbN3ba1nmUHMBkfN'
output = 'paragraph_with_txt_embeddings.parquet'
gdown.download(url, output, quiet=False)

url = 'https://drive.google.com/uc?id=15erTN3Fqcr2VlaSmRPClFf0B5-EUuWxg'
output = 'processed_database_parquet_ceebios_plos_database_parquet_20220613.parquet'
gdown.download(url, output, quiet=False)