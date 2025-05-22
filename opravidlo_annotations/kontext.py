"""
Kontext API documentation: https://github.com/czcorpus/kontext/wiki/API-Creating-a-concordance
limits: 12 requests/second; 5000 requests/day
"""

import pickle
import logging
import json

import requests

from opravidlo_annotations import settings

logging.basicConfig(level=logging.INFO)
cookies_file = "cookies.pickle"
kontext_api_point = "https://korpus.cz/kontext-api/v0.17/"


def setup_session() -> requests.Session:
    """
    Create a session with loaded or refreshed cookies and log in to kontext with personal token.

    Returns:
        requests.Session: Authenticated session with valid cookies.
    """
    session = requests.Session()
    try:
        with open(cookies_file, "rb") as f:
            session.cookies.update(pickle.load(f))
    except FileNotFoundError:
        logging.info(f"No existing cookies found at '{cookies_file}, logging in with access token.")

    response = session.post("https://korpus.cz/login", data={"personal_access_token": settings.KONTEXT_TOKEN})
    if response.status_code != 200:
        raise RuntimeError("Login failed or token is invalid")

    with open(cookies_file, "wb") as f:
        pickle.dump(session.cookies, f)

    return session



def submit_query(session: requests.Session, corpus_name: str, query: str, shuffle: bool=True) -> str:
    """
    Submit a concordance query.

    Args:
        session (requests.Session): Authenticated session.
        corpus_name (str): Corpus name, e.g. "syn2015".
        query (str): CQL query.
        shuffle (bool, optional): Shuffle the results. Defaults to True. It negatively affects performance.
    Returns:
        str: The concordance persistence operation ID.
    """
    if shuffle:
        shuffle_int = 1
    else:
        shuffle_int = 0

    query = "[word=\".*\"]"*20+query+"[word=\".*\"]"*20     # workaround: increases the left and the right context

    request_body = {
        "type": "concQueryArgs",
        "maincorp": corpus_name,
        "usesubcorp": None,
        "viewmode": "kwic",
        "pagesize": 500,                # the number of displayed concordances
        "attrs": ["word"],              # a list of KWIC's positional attributes to be retrieved
        "ctxattrs": [],                 # a list of non-KWIC positional attributes to be retrieved
        "attr_vmode": "visible-kwic",
        "base_viewattr": "word",
        "structs": ["text", "p", "g"],
        "refs": [],
        "fromp": 0,
        "shuffle": shuffle_int,
        "queries": [
            {
                "qtype": "advanced",
                "corpname": corpus_name,
                "query": query,
                "pcq_pos_neg": "pos",
                "include_empty": False,
                "default_attr": "word"  # a positional attribute applied for simplified CQL expressions (e.g., with default_attr="word" one can write "foo" instead of [word="foo"])
            }
        ],
        "text_types": {},
        "context": {
            "fc_lemword_wsize": [-5, 5],
            "fc_lemword": "",
            "fc_lemword_type": "all",
            "fc_pos_wsize": [-5, 5],
            "fc_pos": [],
            "fc_pos_type": "all"
        },
        "async": True
    }

    response = session.post(f"{kontext_api_point}/query_submit?format=json", params={"format": "json"}, json=request_body)
    response.raise_for_status()
    response_json = response.json()

    return response_json["conc_persistence_op_id"]


def fetch_concordances_by_id(session: requests.Session, op_id: str) -> dict:
    """
    Fetch and return the concordance view.

    Args:
        session (requests.Session): Authenticated session.
        op_id (str): Concordance persistence operation ID.

    Returns:
        dict: Concordances in JSON.
    """
    response = session.get(f"{kontext_api_point}/view", params={
        "format": "json",
        "q": f"~{op_id}",
        "pagesize": 500,
    })
    response.raise_for_status()
    return response.json()


def print_json(data: dict, indent: int = 4) -> None:
    """
    Print JSON data with nice indentation.

    Args:
        data (dict): The JSON data to print.
        indent (int, optional): Number of spaces for indentation. Defaults to 4.
    """
    print(json.dumps(data, indent=indent, ensure_ascii=False))
