import pickle
import logging

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


def submit_query(session: requests.Session) -> str:
    """
    Submit a concordance query.

    Args:
        session (requests.Session): Authenticated session.

    Returns:
        str: The concordance persistence operation ID.
    """
    request_body = {
        "type": "concQueryArgs",
        "maincorp": "syn2015",
        "usesubcorp": None,
        "viewmode": "kwic",
        "pagesize": 40,
        "attrs": ["word", "tag"],
        "attr_vmode": "visible-kwic",
        "base_viewattr": "word",
        "ctxattrs": [],
        "structs": ["text", "p", "g"],
        "refs": [],
        "fromp": 0,
        "shuffle": 0,
        "queries": [
            {
                "qtype": "advanced",
                "corpname": "syn2015",
                "query": "[word=\"celou\"] [lemma=\"pravda\"]",
                "pcq_pos_neg": "pos",
                "include_empty": False,
                "default_attr": "word"
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
        "async": False
    }

    response = session.post(f"{kontext_api_point}/query_submit?format=json", params={"format": "json"}, json=request_body)
    response.raise_for_status()
    response_json = response.json()

    return response_json["conc_persistence_op_id"]


def view_concordance(session: requests.Session, op_id: str) -> dict:
    """
    Fetch and return the concordance view.

    Args:
        session (requests.Session): Authenticated session.
        op_id (str): Concordance persistence operation ID.

    Returns:
        dict: Concordance result JSON.
    """
    response = session.get(f"{kontext_api_point}/view", params={"format": "json", "q": f"~{op_id}"})
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    session = setup_session()
    op_id = submit_query(session)
    concordance = view_concordance(session, op_id)
    print(concordance)
