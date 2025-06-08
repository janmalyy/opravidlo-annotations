from opravidlo_annotations.settings import FILES_DIR
from opravidlo_annotations.kontext import setup_session, fetch_concordances_by_id, submit_query
from opravidlo_annotations.concordance2annotation import correct_punctuation, extract_sentence_with_target, \
    add_annotation_to_sentence
from opravidlo_annotations.sketch_engine import get_concordances_from_sketch
from opravidlo_annotations.utils import concordances2text, count_correct_variants_in_json, \
    count_correct_variants_in_txt, remove_duplicates
from opravidlo_annotations.query_logs import log_the_query, generate_text_readme


def generate_concordances(corpus_manager: str, corpus_name: str, target: str, variants: list[str], query: str,
                          number_of_concordances: int, filename: str, is_target_valid: bool) -> list[str]:
    """
    corpus_manager (str): either "sketch" or "kontext"
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

    number_of_concordances (int): how many concordances will be downloaded


    is_target_valid (bool): set to True if it is likely that the target is the correct version in the sentence
    """
    # get the result from the corpus by API
    if corpus_manager == "kontext":
        session = setup_session()
        op_id = submit_query(session, corpus_name, query, number_of_concordances, shuffle=True)
        result = fetch_concordances_by_id(session, op_id, number_of_concordances)

    elif corpus_manager == "sketch":
        result = get_concordances_from_sketch(corpus_name, query, number_of_concordances)

    else:
        raise ValueError(f"Unknown corpus manager: {corpus_manager}. Choose either 'sketch' or 'kontext'.")

    if not result["Lines"]:
        raise ValueError(f"No concordances found in: manager: '{corpus_manager}', corpus: '{corpus_name}'."
                         f"(Are you sure that you used correct tagging system?)")

    # extract complete concordances as strings from result
    concordances = []

    for line in result["Lines"]:
        if corpus_manager == "kontext":
            left = [line["Left"][0]["str"]]
            kwic = [line["Kwic"][0]["str"]]
            right = [line["Right"][0]["str"]]
        else:  # sketch
            def _extract_text(parts: list) -> list:
                return [item["str"] for item in parts if "str" in item]
            left = _extract_text(line["Left"])
            kwic = _extract_text(line["Kwic"])
            right = _extract_text(line["Right"])

        concordance = left + kwic + right
        concordances.append(" ".join(concordance))

    # correct sentences and transform them into annotations
    for i in range(len(concordances)):
        concordance = concordances[i]
        concordance = correct_punctuation(concordance)
        concordance = extract_sentence_with_target(concordance, target)
        concordance = add_annotation_to_sentence(concordance, target, variants, is_target_valid)
        concordances[i] = concordance
        print(concordance)
    print()
    return concordances


def check(filename: str) -> None:
    """
    Remove duplicates and then check the proportion of variants and whether the queries
    (and especially 'number of concordances' variable) are same in the JSON readme and in the real text.
    """
    remove_duplicates(filename)
    print("json: ", count_correct_variants_in_json(FILES_DIR / f"README_{filename}.json"))
    print("txt: ", count_correct_variants_in_txt(FILES_DIR / f"data_zajmena_{filename}.txt"))
    print()


if __name__ == "__main__":
    # set up the variables
    corpus_manager = "sketch"
    corpus_name = "cstenten_all_mj2"
    target = "jež"
    variants = ["jenž"]
    # The query is case-sensitive! Remember.
    # Kontext: 1. slovní druh - 2. určení druhu - 3. rod - 4. číslo - 5. pád - 6. přivl. rod - 7. přivl. číslo - 8. osoba - 9. čas
    query = '[word="jež"]'
    number_of_concordances = 5
    # filename (str): filename to write the annotations into. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
    filename = "jenž_společný"
    is_target_valid = False


    concordances = generate_concordances(corpus_manager, corpus_name, target, variants,
                                         query, number_of_concordances, filename, is_target_valid)

    # save the concordances into the file
    # concordances2text(filename, concordances)

    # log the query and all important variables into JSON README file
    # the 'number_of_concordances' parameter should be later adjusted manually because you don't use every concordance you downloaded
    # log_the_query(filename, corpus_name, query, number_of_concordances, target, variants, is_target_valid)

    # check(filename)

    # generate_text_readme(FILES_DIR / f"README_{filename}.json")
