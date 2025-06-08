"""
Sketch engine API documentation: https://www.sketchengine.eu/documentation/api-documentation/
"""
import requests

from opravidlo_annotations import settings
from opravidlo_annotations.utils import print_json

base_url = "https://api.sketchengine.eu/bonito/run.cgi/concordance"

params = {
    "corpname": "preloaded/cstenten23_mj2",     # preloaded/cstenten_all_mj2 is another great option, it is the biggest one
    "q": 'q[lc="auto"]',
    "qtype": "cql",
    "format": "json",
    "asyn": 1
}

response = requests.get(base_url, params=params, auth=(settings.SKETCH_ENGINE_USERNAME, settings.SKETCH_ENGINE_TOKEN))
data = response.json()
print(print_json(data))
