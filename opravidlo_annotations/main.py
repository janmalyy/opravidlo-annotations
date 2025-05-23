from opravidlo_annotations.kontext import setup_session, fetch_concordances_by_id, submit_query
from opravidlo_annotations.concordance2annotation import correct_punctuation, extract_sentence_with_target, \
    add_annotation_to_sentence
from opravidlo_annotations.utils import concordances2text, log_the_query


if __name__ == "__main__":
    corpus_name = "syn2015"
    target = "jejich"
    variants = ["jejích", "jejího"]
    query = f"[word=\"{target}\"]"
    number_of_concordances = 125
    filename = target
    is_target_valid = True
    is_from_corpus = True

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
        concordance = add_annotation_to_sentence(concordance, target, variants,
                                                 is_target_valid, is_from_corpus)
        concordances[i] = concordance
        print(concordance)

    concordances2text(filename, concordances)
    log_the_query(filename, corpus_name, query, number_of_concordances, target, variants, is_target_valid, is_from_corpus)

