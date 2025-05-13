"""
Sketch engine API documentation: https://www.sketchengine.eu/documentation/api-documentation/
"""

import requests

from opravidlo_annotations import settings

base_url = 'https://api.sketchengine.eu/bonito/run.cgi'
data = {
 'corpname': 'preloaded/bnc2',
 'format': 'json',
 'lemma': 'book',
 'lpos': '-v',
}
d = requests.get(base_url + '/wsketch?corpname=%s' % data['corpname'], params=data, auth=(settings.SKETCH_ENGINE_USERNAME, settings.SKETCH_ENGINE_TOKEN)).json()
print("There are %d grammar relations for %s%s (lemma+PoS) in corpus %s." % (
    len(d['Gramrels']), data['lemma'], data['lpos'], data['corpname']))
