from bloom_filter import BloomFilter
from scrapy.utils.job import job_dir
from scrapy.dupefilters import BaseDupeFilter
import logging 
from pathlib import Path 
import pickle

class BLOOMDupeFilter(BaseDupeFilter):
    """Request Fingerprint duplicates filter"""

    def __init__(self, path=None):
        self.file = Path("./bloom.sav")
        if self.file.exists():
            logging.log(logging.INFO, "Get existing bloom filter")
            with self.file.open(mode="rb") as f:
                self.fingerprints = pickle.load(f)
        else:
            self.fingerprints = BloomFilter(200000, 0.00001)

    @classmethod
    def from_settings(cls, settings):
        return cls(job_dir(settings))

    def request_seen(self, request):
        fp = request.url
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)

    def close(self, reason):
        logging.log(logging.INFO, "Save bloom filter")
        with self.file.open(mode="wb") as f:
            f.write(pickle.dumps(self.fingerprints))
        self.fingerprints = None