from opravidlo_annotations.settings import FILES_DIR
from opravidlo_annotations.kontext import setup_session, fetch_concordances_by_id, submit_query
from opravidlo_annotations.concordance2annotation import correct_punctuation, extract_sentence_with_target, \
    add_annotation_to_sentence
from opravidlo_annotations.utils import concordances2text, count_correct_variants_in_json, \
    count_correct_variants_in_txt, remove_duplicates
from opravidlo_annotations.query_logs import log_the_query, generate_text_readme


def generate_and_save_query(corpus_name: str, target: str, variants: list[str], query: str,
                            number_of_concordances: int, filename: str, is_target_valid: bool) -> None:
    """
    corpus_name (str): Currently, it works only with the Kontext API. However, not all corpora are available.
                        It seems like it works only with small corpus. Possible OK values = syn2020, syn2015, syn2009pub, (other synYEAR options), capek_uplny, orwell, ksk-dopisy, ksp, net...
                        Unfortunately, online2_archive, synv13 (and other versioned syn corpora) are not allowed.
                        So, "net" is the only option(?) to look for natural errors, it seems.
                        Available corpora: https://wiki.korpus.cz/doku.php/cnk:uvod

    target (str): the word / word phrase that you are concerned about.
                  Both target and target variants should not be regular expressions because they are written as is into annotations.

    variants (list[str]): the second possible word / words which can occur at the same place as the target.
                          It is a list; this is an advantage if the target is correct, and there are multiple equally bad other options – a randomly picked variant is then placed into the resulting annotation.

    query (str): same CQL query as in the web interface. Mind that there have to be single quotes around the expression and double quotes inside to properly parse it.
                 Note that the query is case-sensitive.

    number_of_concordances (int): how many concordances will be downloaded

    filename (str): filename to write the annotations into. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.

    is_target_valid (bool): set to True if it is likely that the target is the correct version in the sentence
    """
    session = setup_session()
    op_id = submit_query(session, corpus_name, query, number_of_concordances)
    result = fetch_concordances_by_id(session, op_id, number_of_concordances)

    if not result["Lines"]:
        raise ValueError("No concordances found.")

    concordances = [each["Left"][0]["str"] + each["Kwic"][0]["str"] + each["Right"][0]["str"]
                    for each in result["Lines"]
                    ]
    for i in range(len(concordances)):
        concordance = concordances[i]
        concordance = correct_punctuation(concordance)
        concordance = extract_sentence_with_target(concordance, target)
        concordance = add_annotation_to_sentence(concordance, target, variants, is_target_valid)
        concordances[i] = concordance
        print(concordance)
    print()

    # save the concordances into the file
    concordances2text(filename, concordances)


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
    corpus_name = "syn2015"
    target = "sebou"
    variants = ["s sebou"]
    # The query is case-sensitive! Remember.
    query = '[word!="s" & word!="se" & tag!="R.*"][word="sebou"]'
    number_of_concordances = 100
    filename = "jejich"
    is_target_valid = True

    # generate_and_save_query(corpus_name, target, variants, query, number_of_concordances, filename, is_target_valid)

    # log the query and all important variables into JSON README file
    # the 'number_of_concordances' parameter should be later adjusted manually because you don't use every concordance you downloaded
    # log_the_query(filename, corpus_name, query, number_of_concordances, target, variants, is_target_valid)

    check(filename)

    # generate_text_readme(FILES_DIR / f"README_{filename}.json")
