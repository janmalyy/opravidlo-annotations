from opravidlo_annotations.kontext import setup_session, fetch_concordances_by_id, submit_query
from opravidlo_annotations.concordance2annotation import correct_punctuation, extract_sentence_with_target, \
    add_annotation_to_sentence
from opravidlo_annotations.utils import concordances2text

if __name__ == "__main__":
    corpus_name = "syn2015"
    target = "jejich"
    variants = ["jejích"]
    query = f"[word=\"{target}\"]"

    session = setup_session()
    op_id = submit_query(session, corpus_name, query)
    result = fetch_concordances_by_id(session, op_id)

    if not result["Lines"]:
        raise ValueError("No concordances found.")

    concordances = [each["Left"][0]["str"] + each["Kwic"][0]["str"] + each["Right"][0]["str"]
                    for each in result["Lines"]
                   ]
    for concordance in concordances:
        concordance = correct_punctuation(concordance)
        concordance = extract_sentence_with_target(concordance, target)
        concordance = add_annotation_to_sentence(concordance, target, variants, is_target_valid=True, is_from_corpus=True)
        print(concordance)

    concordances2text(target, concordances, False)
