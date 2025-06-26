import re
import random as rd
from collections.abc import Callable

import nltk

nltk.download("punkt")


def correct_punctuation(text: str) -> str:
    """
    Corrects punctuation in a string. Corrects the three dots, hyphen to dash and removes any trailing whitespaces before or after the punctuation mark.
    """
    three_dots_corrected = re.sub(r'\.\.\.', r'…', text)
    two_spaces_corrected = re.sub(r'  ', r' ', three_dots_corrected)
    dash_corrected = re.sub(r' - ', r' – ', two_spaces_corrected)
    removed_before = re.sub(r'\s+([.,\]?!:;“"…)¨«])', r"\1", dash_corrected)
    removed_after = re.sub(r'([„\[("»°])\s+', r"\1", removed_before)
    return removed_after


def remove_left_trailing_chars(sentence: str) -> str:
    """
    Remove characters before the start of the sentence. This means any characters before the capital letter.
    If the capital letter is not found or is found after a long distance (distance is set to 10)
    from the start of the sentence, the sentence is returned unchanged. - The stopper is set because if there is
    no capital letter in the first 10 chars, it probably indicates that it is a long sentence without
    a start, and we don't want to remove it.

    Returns: Sentence without left trailing characters.
    """
    # beginning of the sentence, then 0-10 times any other character than „ or ( and then a big letter
    pattern = r'^[^\(„]{0,10}?([A-ZŠČŘŽŠĎŤŇ])'
    match = re.search(pattern, sentence)
    if match:
        start_index = match.start(1)
        return sentence[start_index:]
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
        pattern = rf"\b{re.escape(target)}\b"
        match = re.search(pattern, sentences[i], flags=re.IGNORECASE)
        if match:
            return remove_left_trailing_chars(sentences[i])

    raise ValueError(f"Target word '{target}' not found in concordance: '{concordance}'.")


def add_annotation_to_sentence(sentence: str, target:str, target_variants:list[str], is_target_valid:bool, construct_target_variant: Callable[[str, str], str]=None) -> str:
    """
    Insert all information for the annotation into the sentence.
    If there are multiple variants of the target, one variant is chosen randomly.
    Args:
        sentence: sentence to be annotated
        target: a word or phrase which was mainly looked up in the corpus
        target_variants: other possible words or phrases which could occur at the same place as target in the sentence
        is_target_valid: whether the target is orthographically correct or not
        construct_target_variant: function which - if is passed - is applied to target_variant and changes it

    Example:
        input: "Stál před jejích chalupou.", "jejích", ["jejich"], False, False
        output: Stál před [*jejích|jejich|corpus*] chalupou.

    Returns: Annotated sentence. The resulting format is:
    beginning_of_the_sentence[*error|valid|corpus*]rest_of_the_sentence
    """
    target_variant = rd.choice(target_variants)
    target_ready_to_regexp = rf"\b{re.escape(target)}\b"

    if construct_target_variant:
        target_variant = construct_target_variant(target, target_variant)
        if is_target_valid:
            return re.sub(target_ready_to_regexp, f"[*{target_variant}|{target}|corpus*]", sentence, flags=re.IGNORECASE)
        else:
            return re.sub(target_ready_to_regexp, f"[*{target}|{target_variant}|corpus*]", sentence, flags=re.IGNORECASE)

    else:
        if is_target_valid:
            return re.sub(target_ready_to_regexp, f"[*{target_variant}|{target}|corpus*]", sentence, flags=re.IGNORECASE)
        else:
            return re.sub(target_ready_to_regexp, f"[*{target}|{target_variant}|corpus*]", sentence, flags=re.IGNORECASE)
