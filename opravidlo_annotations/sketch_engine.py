"""
Sketch engine API documentation: https://www.sketchengine.eu/documentation/api-documentation/
"""
import requests

from opravidlo_annotations import settings


def get_concordances_from_sketch(corpus_name: str, query: str, number_of_concordances: int) -> dict:
    base_url = "https://api.sketchengine.eu/bonito/run.cgi/concordance"

    params = {
        "corpname": f"preloaded/{corpus_name}",
        "q": f'q{query}',
        "pagesize": number_of_concordances,
        "kwicleftctx": -20,
        "kwicrightctx": 20,
        "qtype": "cql",
        "format": "json",
        "asyn": 1
    }

    response = requests.get(base_url, params=params, auth=(settings.SKETCH_ENGINE_USERNAME, settings.SKETCH_ENGINE_TOKEN))
    response.raise_for_status()
    return response.json()
