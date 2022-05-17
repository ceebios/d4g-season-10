import os 
import json
import pkgutil
import logging

path = "{}/google-cloud-storage-credentials.json".format(os.getcwd())

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

