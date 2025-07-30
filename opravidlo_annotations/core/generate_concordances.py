import random as rd
from collections.abc import Callable

import requests

from opravidlo_annotations.core.concordance2annotation import correct_punctuation, extract_sentence_with_target, \
    add_annotation_to_sentence, construct_target_from_code
from opravidlo_annotations.api.kontext import setup_session, submit_query, fetch_concordances_by_id
from opravidlo_annotations.api.sketch_engine import get_concordances_from_sketch




def _extract_kontext_text(line: dict) -> str:
    """
    Extract text from a Kontext concordance line.

    Args:
        line: A concordance line from Kontext

    Returns:
        Extracted text as a string
    """
    left = [line["Left"][0]["str"]]
    kwic = [line["Kwic"][0]["str"]]
    right = [line["Right"][0]["str"]]
    return " ".join(left + kwic + right)


def _extract_sketch_text(line: dict) -> str:
    """
    Extract text from a Sketch Engine concordance line.

    Args:
        line: A concordance line from Sketch Engine

    Returns:
        Extracted text as a string
    """
    left = [item["str"] for item in line["Left"] if "str" in item]
    kwic = [item["str"] for item in line["Kwic"] if "str" in item]
    right = [item["str"] for item in line["Right"] if "str" in item]
    return " ".join(left + kwic + right)


def _check_result_has_lines(result: dict, corpus_manager: str, corpus_name: str) -> None:
    """
    Check if the result has lines and raise a consistent error message if not.

    Args:
        result: The result to check
        corpus_manager: The corpus manager used
        corpus_name: The name of the corpus

    Raises:
        ValueError: If the result has no lines
    """
    if not result.get("Lines"):
        raise ValueError(f"No concordances found in: manager: '{corpus_manager}', corpus: '{corpus_name}'."
                         f"(Are you sure that you used correct tagging system?)")


def _fetch_kontext_concordances(corpus_name: str, query: str, number_of_concordances_to_fetch: int) -> list[str]:
    """
    Fetch concordances from a Kontext corpus.

    Args:
        corpus_name: The name of the corpus
        query: The query to search for
        number_of_concordances_to_fetch: The number of concordances to fetch

    Returns:
        A list of concordance strings
    """
    session = setup_session()
    op_id = submit_query(session, corpus_name, query, number_of_concordances_to_fetch, shuffle=True)
    result = fetch_concordances_by_id(session, op_id, number_of_concordances_to_fetch)

    _check_result_has_lines(result, "kontext", corpus_name)

    concordances = []
    for line in result["Lines"]:
        concordances.append(_extract_kontext_text(line))

    return concordances


def _fetch_sketch_concordances(corpus_name: str, query: str, number_of_concordances_to_fetch: int) -> list[str]:
    """
    Fetch concordances from a Sketch Engine corpus.

    Args:
        corpus_name: The name of the corpus
        query: The query to search for
        number_of_concordances_to_fetch: The number of concordances to fetch

    Returns:
        A list of concordance strings
    """
    result = get_concordances_from_sketch(corpus_name, query, number_of_concordances_to_fetch)

    _check_result_has_lines(result, "sketch", corpus_name)

    concordances = []
    for line in result["Lines"]:
        concordances.append(_extract_sketch_text(line))

    return concordances


def _fetch_combo_concordances(query: str, number_of_concordances_to_fetch: int) -> list[str]:
    """
    Fetch concordances from multiple corpora from Kontext API using the "combo" approach.

    Args:
        query: The query to search for
        number_of_concordances_to_fetch: The number of concordances to fetch

    Returns:
        A list of concordance strings
    """
    session = setup_session()
    corpora_names = ["syn2015", "net", "syn2013pub", "parlcorp"]
    map_numbers_to_corpora = {
        "syn2015": 0.5,
        "net": 0.2,
        "syn2013pub": 0.2,
        "parlcorp": 0.1
    }

    actual_numbers_of_concordances_to_fetch_dict = {
        name: max(1, int(number_of_concordances_to_fetch * map_numbers_to_corpora[name]))
        for name in corpora_names
    }

    results = []
    for name in corpora_names:
        try:
            print(
                f"Fetching from corpus: {name} ({actual_numbers_of_concordances_to_fetch_dict[name]} concordances)")
            op_id = submit_query(session, name, query, actual_numbers_of_concordances_to_fetch_dict[name],
                                 shuffle=True)
            result = fetch_concordances_by_id(session, op_id, actual_numbers_of_concordances_to_fetch_dict[name])
            if not result["Lines"]:
                print(f"No results from {name}")
                continue
            results.append(result)
        except requests.HTTPError as e:
            print(f"Failed for corpus '{name}': {e}")
            continue

    concordances = []
    for result in results:
        for line in result["Lines"]:
            concordances.append(_extract_kontext_text(line))

    rd.shuffle(concordances)
    return concordances


def _process_and_annotate_concordances(concordances: list[str], to_be_target: str, variants: list[str], is_target_valid: bool,
                                       is_target_regexp:bool, variants_weights: list[float] = None,
                                       construct_target_variant: Callable[[str, str], str] = None) -> list[str]:
    processed_concordances = []
    for concordance in concordances:
        if is_target_regexp:
            target = construct_target_from_code(to_be_target, concordance)
            if target is None:
                continue
        else:
            target = to_be_target

        concordance = extract_sentence_with_target(concordance, target)
        concordance = add_annotation_to_sentence(concordance, target, variants, is_target_valid,
                                                 variants_weights, construct_target_variant)
        concordance = correct_punctuation(concordance)
        processed_concordances.append(concordance)
        print(concordance)

    print()
    return processed_concordances


def generate_concordances(corpus_manager: str, corpus_name: str, target: str, variants: list[str], query: str,
                          number_of_concordances_to_fetch: int, is_target_valid: bool,
                          is_target_regexp: bool, variants_weights: list[float] = None,
                          construct_target_variant: Callable[[str, str], str] = None) -> list[str]:
    """
    Generate concordances from a corpus and annotate them.

    Args:
        corpus_manager (str): "sketch" or "kontext" or "combo"; "combo" means sampling from multiple corpora from kontext
        corpus_name (str):
                           if corpus_manager == "kontext":
                           Not all corpora from Kontext API are available.
                           It seems like it works only with small corpus. Possible OK values = syn2020, syn2015, syn2009pub, (other synYEAR options), capek_uplny, orwell, ksk-dopisy, ksp, net...
                           Unfortunately, online2_archive, synv13 (and other versioned syn corpora) are not allowed.
                           So, "net" is the only option(?) to look for natural errors, it seems.
                           Available corpora from Kontext API: https://wiki.korpus.cz/doku.php/cnk:uvod
                           ---
                           if corpus_manager == "sketch":
                           Possible good values: cstenten_all_mj2 (cstenten 12 + 17 + 19; 11.7 billion of tokens), cstenten23_mj2 (5.4 billion of tokens)

        target (str): the word / word phrase that you are concerned about.
                      Both target and target variants should not be regular expressions because they are written as is into annotations.

        variants (list[str]): the second possible word / words which can occur at the same place as the target.
                              It is a list; this is an advantage if the target is correct, and there are multiple equally bad other options – a randomly picked variant is then placed into the resulting annotation.

        query (str): Important!: Sketch engine uses tagging system from Brno (e.g., 'k1' for noun).
                     Same CQL query as in the web interface. Mind that there have to be single quotes around the expression and double quotes inside to properly parse it.
                     Note that the query is case-sensitive.

        number_of_concordances_to_fetch (int): how many concordances will be downloaded

        is_target_valid (bool): set to True if it is likely that the target is the correct version in the sentence

        is_target_regexp (bool): True means we don't look for a concrete word/phrase but for a regexp pattern

        variants_weights: list of weights to change the distribution of variants

        construct_target_variant: function which - if is passed - is applied to target_variant and changes it

    Returns:
        list[str]: List of processed and annotated concordances
    """
    if corpus_manager == "combo":
        concordances = _fetch_combo_concordances(query, number_of_concordances_to_fetch)

    elif corpus_manager == "kontext":
        concordances = _fetch_kontext_concordances(corpus_name, query, number_of_concordances_to_fetch)

    elif corpus_manager == "sketch":
        concordances = _fetch_sketch_concordances(corpus_name, query, number_of_concordances_to_fetch)
    else:
        raise ValueError(f"Unknown corpus manager: {corpus_manager}. Choose either 'sketch', 'kontext', or 'combo'.")

    return _process_and_annotate_concordances(concordances, target, variants, is_target_valid, is_target_regexp, variants_weights, construct_target_variant)
