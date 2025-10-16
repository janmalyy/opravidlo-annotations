import re
import logging
import random as rd
from collections.abc import Callable

import nltk

nltk.download("punkt")

logging.basicConfig(level=logging.INFO)

def correct_punctuation(text: str) -> str:
    """
    Corrects punctuation in a string. Corrects multiple typographical details.
    """
    three_dots_corrected = re.sub(r'\.\.\.', r'…', text)
    two_spaces_corrected = re.sub(r'  ', r' ', three_dots_corrected)
    li_corrected = re.sub(r' - li', ' -li', two_spaces_corrected)
    dash_corrected = re.sub(r' - ', r' – ', li_corrected)
    removed_before = re.sub(r'\s+([.,\]}?!:;“…)+¨«‘])', r"\1", dash_corrected)
    removed_after = re.sub(r'([„\[{(»°+‚])\s+', r"\1", removed_before)
    quotation_mark_corrected = re.sub(r'"([ $,.?!])', r"“\1", removed_after)
    quotation_mark_corrected = re.sub(r' "', r" „", quotation_mark_corrected)
    return quotation_mark_corrected


def remove_left_trailing_chars(sentence: str) -> str:
    """
    Remove characters before the start of the sentence. This means any characters before the capital letter.
    If the capital letter is not found or is found after a long distance (distance is set to 10)
    from the start of the sentence, the sentence is returned unchanged. - The stopper is set because if there is
    no capital letter in the first 10 chars, it probably indicates that it is a long sentence without
    a start, and we don't want to remove it.
    Remove also this pattern („ “) from the beginning of the sentence.

    Returns: Sentence without left trailing characters.
    """
    # beginning of the sentence, then 0-10 times any other character than „ or ( and then a big letter
    pattern = r'^[^\(„]{0,10}?([A-ZŠČŘŽŠĎŤŇ])'
    match = re.search(pattern, sentence)
    if match:
        start_index = match.start(1)
        return sentence[start_index:]
    pattern = r'^„ ?“'
    match = re.search(pattern, sentence)
    if match:
        return sentence[match.end():]
    return sentence


def extract_sentence_with_target(concordance: str, target: str) -> str|None:
    """
    Extracts a single sentence containing the target word from the given concordance text.

    This function searches the provided concordance text for a sentence that includes
    the specified target word. A sentence is assumed to end with a period, question mark,
    or exclamation mark. If the target word is not found within any sentence, the function
    returns None.

    Args:
        concordance: A string representing the text containing multiple sentences.
        target: The word to search for within the concordance text.

    Returns:
        A string representing the single sentence containing the target word, or None
        if the target word is not found.
    """
    if not concordance or not target:
        raise ValueError("Empty input. Please provide valid concordance and target.")

    sentences = nltk.sent_tokenize(concordance)
    for i in range(len(sentences)):
        if re.search(r"[”“]", sentences[i]) and not re.search(r"„", sentences[i]):
            sentences[i] = "„" + sentences[i]
        pattern = rf"{re.escape(target.strip())}"
        match = re.search(pattern, sentences[i], flags=re.IGNORECASE)
        if match:
            return remove_left_trailing_chars(sentences[i])

    raise ValueError(f"Target word '{target}' not found in concordance: '{concordance}'.")


def add_annotation_to_sentence(sentence: str, target:str, rest:str, target_variants:list[str], is_target_valid:bool,
                               variants_weights: list[float]= None, construct_target_variant: Callable[[str, str], str]=None) -> str:
    """
    Insert all information for the annotation into the sentence.
    If there are multiple variants of the target, one variant is chosen randomly.
    Args:
        sentence: sentence to be annotated
        target: a word or phrase which was mainly looked up in the corpus
        rest: space or punctuation mark following immediately the target
        target_variants: other possible words or phrases which could occur at the same place as target in the sentence
        is_target_valid: whether the target is orthographically correct or not
        variants_weights: list of weights to change the distribution of variants
        construct_target_variant: function which - if is passed - is applied to target_variant and changes it

    Example:
        input: "Stál před jejích chalupou.", "jejích", ["jejich"], False, False
        output: Stál před [*jejích|jejich|corpus*] chalupou.

    Returns: Annotated sentence. The resulting format is:
    beginning_of_the_sentence[*error|valid|corpus*]rest_of_the_sentence
    """
    if variants_weights is None:
        target_variant = rd.choice(target_variants)
    else:
        if len(target_variants) != len(variants_weights):
            raise ValueError(f"Target variants and weights do not match, they have different length."
                             f"Variants: {len(target_variants)}, Weights: {len(variants_weights)}")
        target_variant = rd.choices(target_variants, variants_weights, k=1)[0]  # [0] is here because choices returns a list, and we want only the string
    if rest is None:
        rest = " "
    target = target.strip()
    target_ready_to_regexp = rf"(?:^| ){re.escape(target)}{re.escape(rest)}"

    if construct_target_variant:
        target_variant = construct_target_variant(target, target_variant)

    if is_target_valid:
        return re.sub(target_ready_to_regexp, f" [*{target_variant}|{target}|corpus*]{rest}", sentence, flags=re.IGNORECASE).strip()
    else:
        return re.sub(target_ready_to_regexp, f" [*{target}|{target_variant}|corpus*]{rest}", sentence, flags=re.IGNORECASE).strip()


def construct_target_from_code(target_code: str, concordance: str) -> tuple[str, str] | tuple[None, None]:
    """
    Given target_code, create regexp and find the real target in concordance.

    Examples:
         target_code = "mi-mi", concordance = "S tvými kamarádkami nechci mít nic společného." -> "tvými kamarádkami "

    Returns: Ready to be used target and the rest after the target (space or punctuation mark)

    """
    parts = target_code.split("-")
    pattern = "".join(rf'(?:^| ){part}\w*[^\w]' for part in parts)  # this has to be changed sometimes
    match = re.search(pattern, concordance, flags=re.IGNORECASE)
    if match:
        target = match.group()[:-1]
        rest = match.group()[-1]
        return target, rest
    else:
        logging.info(f"Concordance: '{concordance}' does not contain a target: '{target_code}'.")
        return None, None


def construct_target_variant_from_code(target: str, target_variant_code:str) -> str:
    """
    Replace the last character of each word in target with a corresponding character in the target_variant.

    Examples:
         target = "těmi dlouhými rukami", target_variant_code = "a-a-a" -> "těma dlouhýma rukama"

    Returns:
        Ready to be used target variant.
    """
    parts = target.strip().split(" ")
    target_variant_code_parts = target_variant_code.split("-")
    modified_parts = []
    for i in range(len(parts)):
        part = re.sub(r"^.....", f"{target_variant_code_parts[i]}", parts[i])
        # part = re.sub(r"(\w)(?=\b)", f"{target_variant_code_parts[i]}", parts[i])       # this has to be changed sometimes
        # part = target.replace("bi", target_variant_code_parts[i])
        modified_parts.append(part)

    return " ".join(modified_parts)
