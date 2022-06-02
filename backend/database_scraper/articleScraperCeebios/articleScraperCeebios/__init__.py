import os 
from pathlib import Path
import json
import pkgutil
import logging

p = Path(__file__).parents[1]
path = "{}/google-cloud-storage-credentials.json".format(str(p.absolute()))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

