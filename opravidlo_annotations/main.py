from opravidlo_annotations.kontext import setup_session, fetch_concordances_by_id, submit_query
from opravidlo_annotations.concordance2annotation import correct_punctuation, extract_sentence_with_target, \
    add_annotation_to_sentence
from opravidlo_annotations.utils import concordances2text, log_the_query


if __name__ == "__main__":
    """
    corpora_name (str): Currently, it works only with the Kontext API. However, not all corpora are available.
                        It seems like it works only with small corpora. Possible OK values = syn2020, syn2015, syn2009pub, (other synYEAR options), capek_uplny, orwell, ksk-dopisy, ksp, net...
                        Unfortunately, online2_archive, synv13 (and other versioned syn corpora) are not allowed.
                        So, "net" is the only option(?) to look for natural errors, it seems.
    
    target (str): the word / word phrase that you are concerned about
    
    variants (list[str]): the second possible word / words which can occur at the same place as the target.
                          It is a list; this is an advantage if the target is correct and there are multiple equally bad other options – a randomly picked variant is then placed into the resulting annotation.
                          
    query (str): same CQL query as in the web interface. Mind that there have to be single quotes around the expression and double quotes inside to properly parse it.
                 Note that the query is case-sensitive.
    
    number_of_concordances (int): how many concordances will be downloaded
    
    filename (str): filename to write the annotations into. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
    
    is_target_valid (bool): set to True if it is likely that the target is the correct version in the sentence
    is_form_corpora (bool): set to False if the error was not found in the corpora and you created it                           
    """
    # set up the variables
    corpora_name = "net"
    target = "jejich"
    variants = ["jejích"]
    query = f'[word="{target}"]'
    number_of_concordances = 125
    filename = target
    is_target_valid = True
    is_from_corpora = True

    # run
    session = setup_session()
    op_id = submit_query(session, corpora_name, query, number_of_concordances)
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
                                                 is_target_valid, is_from_corpora)
        concordances[i] = concordance
        print(concordance)

    # store the concordances into the file
    concordances2text(filename, concordances)

    # Logs the query and all important variables into JSON README file. Doesn't work fully yet. It is better to not use now.
    # log_the_query(filename, corpora_name, query, number_of_concordances, target, variants, is_target_valid, is_from_corpora)

