from opravidlo_annotations.core.generate_concordances import generate_concordances
from opravidlo_annotations.settings import FILES_DIR
from opravidlo_annotations.utils.utils import save_concordances_to_file
from opravidlo_annotations.utils.query_logs import log_the_query, generate_text_readme


if __name__ == "__main__":
    corpus_manager = "combo"
    corpus_name = "combo"
    target = "jí"
    variants = ["ji"]

    # The query is case-sensitive! Remember.
    # Kontext canonical order: 1. slovní druh - 2. určení druhu - 3. rod - 4. číslo - 5. pád - 6. přivl. rod - 7. přivl. číslo - 8. osoba - 9. čas (https://wiki.korpus.cz/doku.php/seznamy:tagy#popis_jednotlivych_pozic_znacky)
    # Sketch engine canonical order: kegncpamdxytzw~ (https://www.sketchengine.eu/tagset-reference-for-czech/)
    query = f'[word="[Jj]í" & lemma="ona|on" & tag="P.FS2.*"]'

    # 'number_of_concordances_to_fetch' says how many concordances to download. However, it is often more than we want to store as some will be deleted.
    # 'number_of_concordances_to_log' is then the number to appear in the log, it is the final desired number of concordances which will be stored.
    number_of_concordances_to_fetch = 40
    number_of_concordances_to_log = 25

    # filename (str): filename to write the annotations into. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
    filename = "ji_ni"
    is_target_valid = True

    concordances = generate_concordances(corpus_manager, corpus_name, target, variants,
                                         query, number_of_concordances_to_fetch, is_target_valid)

    save_concordances_to_file(filename, concordances)

    log_the_query(filename, corpus_name, query, number_of_concordances_to_log, target, variants, is_target_valid)

    # check(filename)

    generate_text_readme(FILES_DIR / f"README_{filename}.json")
