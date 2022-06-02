from bloom_filter import BloomFilter
import pickle


liFilters = [("filterXML", 100000), ("filterPDF", 100000), ("filterIMG", 100000)]
for filt in liFilters:
    bloom = BloomFilter(max_elements=filt[1], error_rate=0.1)
    with open(filt[0]+".pkl", mode="wb") as f:
        d = f.write(pickle.dumps(bloom))

    
    # def __init__(self, BLOOM_XML):
    #     self.BLOOM_XML = BLOOM_XML

    # @classmethod
    # def from_crawler(cls, crawler):
    #     ## pull in information from settings.py
    #     return cls(
    #         BLOOM_XML=crawler.settings.get('BLOOM_XML')
    #     )
    # def accepts(self, item):
    #     field = "doi" 
    #     if field in item and not item[field] in self.filter:
    #         return True
    #     return False

    # def open_spider(self, spider):
    #     ## initializing spider
    #     ## opening db connection
    #     with open(self.BLOOM_XML, mode="rb") as f:
    #         self.filter = pickle.loads(f.read())
    
    # def close_spider(self, spider):
    #     ## clean up when spider is closed
    #     with open(self.BLOOM_XML, mode="wb") as f:
    #         f.write(pickle.dumps(self.filter))
    
    # ## Add bloom filter for select unique id

