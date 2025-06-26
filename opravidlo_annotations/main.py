import re

from opravidlo_annotations.core.generate_concordances import generate_concordances
from opravidlo_annotations.settings import FILES_DIR
from opravidlo_annotations.utils.utils import save_concordances_to_file, check
from opravidlo_annotations.utils.query_logs import log_the_query, generate_text_readme


def construct_target_variant(target: str, target_variant_code:str) -> str:
    """
    Replace the last character of each word in target with a corresponding character in the target_variant.

    Examples:
         target = "těmi dlouhými rukami", target_variant = "aaa" -> "těma dlouhýma rukama"

    Returns:
        Ready to be used target variant.
    """
    parts = target.split(" ")
    modified_parts = []
    for i in range(len(parts)):
        part = re.sub(r"(\w)(?=\b)", f"{target_variant_code[i]}", parts[i])
        modified_parts.append(part)

    return " ".join(modified_parts)


if __name__ == "__main__":

    corpus_manager = "kontext"
    corpus_name = "syn2020"     # cstenten_all_mj2, cstenten23_mj2
    target = "ia"
    variants = ["aa"]

    # The query is case-sensitive! Remember.
    # Kontext canonical order: 1. slovní druh - 2. určení druhu - 3. rod - 4. číslo - 5. pád - 6. přivl. rod - 7. přivl. číslo - 8. osoba - 9. čas (https://wiki.korpus.cz/doku.php/seznamy:tagy#popis_jednotlivych_pozic_znacky)
    # Sketch engine canonical order: kegncpamdxytzw~ (https://www.sketchengine.eu/tagset-reference-for-czech/)
    query = f'[(tag="A.*" | tag="P[S8].*" | tag="C[rw]" | lemma="tři|čtyři") & word=".*i"][word=".*a" & tag="N.*"]'

    # 'number_of_concordances_to_fetch' says how many concordances to download. However, it is often more than we want to store as some will be deleted.
    # 'number_of_concordances_to_log' is then the number to appear in the log, it is the final desired number of concordances which will be stored.
    number_of_concordances_to_fetch = 10
    number_of_concordances_to_log = 25

    # filename (str): filename to write the annotations into. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
    filename = "ji_ni"
    is_target_valid = True

    concordances = generate_concordances(corpus_manager, corpus_name, target, variants,
                                         query, number_of_concordances_to_fetch, is_target_valid, construct_target_variant)

    # save_concordances_to_file(filename, concordances)

    # log_the_query(filename, corpus_name, query, number_of_concordances_to_log, target, variants, is_target_valid)

    check(filename)

    generate_text_readme(FILES_DIR / f"README_{filename}.json")
