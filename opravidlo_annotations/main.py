import os
import subprocess

from opravidlo_annotations.core.concordance2annotation import construct_target_variant_from_code
from opravidlo_annotations.core.generate_concordances import generate_concordances
from opravidlo_annotations.settings import FILES_DIR, DATA_CATEGORY
from opravidlo_annotations.utils.utils import save_concordances_to_file, check, save_concordances_to_word
from opravidlo_annotations.utils.query_logs import log_the_query, generate_text_readme


if __name__ == "__main__":
    corpus_manager = "sketch"
    corpus_name = "cstenten_all_mj2"     # cstenten_all_mj2, cstenten23_mj2
    target = "nevybi"
    variants = ["nevyby"]
    if target == variants[0]:
        raise ValueError("Target and variant are equal, correct it.")
    variants_weights = [1]
    is_target_code = True

    # The query is case-sensitive! Remember.
    # Kontext canonical order: 1. slovní druh - 2. určení druhu - 3. rod - 4. číslo - 5. pád - 6. přivl. rod - 7. přivl. číslo - 8. osoba - 9. čas (https://wiki.korpus.cz/doku.php/seznamy:tagy#popis_jednotlivych_pozic_znacky)
    # Sketch engine canonical order: kegncpamdxytzw~ (https://www.sketchengine.eu/tagset-reference-for-czech/)
    query = '[lemma="vybít" & lc="nevybi.*" & tag=".*mA.*"]'
    # query = '[lemma!="vztek" & lemma!="zlost" & lemma!="energie"]{5}[lemma="vybýt" & lc="nevyby.*" & tag=".*mA.*"][lemma!="vztek" & lemma!="zlost" & lemma!="energie"]{5}'
    # query = '[lc="nevybít"]'
    # 'number_of_concordances_to_fetch' says how many concordances to download. However, it is often more than we want to store as some will be deleted.
    # 'number_of_concordances_to_log' is then the number to appear in the log, it is the final desired number of concordances which will be stored.
    if corpus_manager == "sketch":
        number_of_concordances_to_fetch = 400
    elif corpus_manager == "kontext":
        number_of_concordances_to_fetch = 80
    number_of_concordances_to_log = 10

    # filename (str): filename to write the annotations into. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
    filename = FILES_DIR.stem
    is_target_valid = True

    if not FILES_DIR.exists():
        os.mkdir(FILES_DIR)
        file_path = FILES_DIR / f"{DATA_CATEGORY}_{filename}.txt"
        with open(file_path, "w") as file:
            file.write("")
        subprocess.Popen(["notepad.exe", file_path])

    concordances = generate_concordances(corpus_manager, corpus_name, target, variants,
                                         query, number_of_concordances_to_fetch, is_target_valid,
                                         is_target_code, variants_weights, construct_target_variant_from_code)
                                         # if target is code, you have to add construct_target_variant_from_code as parameter

    # save_concordances_to_file(filename, concordances)
    # save_concordances_to_word(concordances)

    # log_the_query(filename, corpus_name, query, number_of_concordances_to_log, target, variants, is_target_valid)

    check(filename)

    generate_text_readme(FILES_DIR / f"README_{filename}.json")
