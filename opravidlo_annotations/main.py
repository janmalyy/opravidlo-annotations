from opravidlo_annotations.kontext import setup_session, fetch_concordances_by_id, submit_query
from opravidlo_annotations.concordance2annotation import correct_punctuation

if __name__ == "__main__":
    corpus_name = "syn2015"
    # query = "[word=\"yea\"]"  # OK
    # query = "\"yea\""         # OK
    # query = "yea"             # NOK
    query = "[word=\"mám\"][word=\"velký\"][word=\"hlad\"]"
    session = setup_session()
    op_id = submit_query(session, corpus_name, query)
    result = fetch_concordances_by_id(session, op_id)

    lines = []
    if not result["Lines"]:
        print("No concordances found.")
    else:
        for each in result["Lines"]:
            lines.append(each["Left"][0]["str"] + each["Kwic"][0]["str"] + each["Right"][0]["str"])
        for line in lines:
            line = correct_punctuation(line)
            print(line)

