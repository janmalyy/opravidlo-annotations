import re
import random as rd

import nltk

nltk.download("punkt")


def correct_punctuation(text: str) -> str:
    """
    Corrects punctuation in a string. It removes any trailing whitespaces before or after the punctuation mark.
    """
    removed_after = re.sub(r'\s+([.,?!:;“"(])', r"\1", text)
    removed_before = re.sub(r'([„)"])\s+', r"\1", removed_after)
    return removed_before


def remove_left_trailing_chars(sentence: str) -> str:
    """
    Remove characters before the start of the sentence. This means any characters before the capital letter.
    If the capital letter is not found or is found after a long distance (distance is set to 10)
    from the start of the sentence, the sentence is returned unchanged. - The stopper is set because if there is
    no capital letter in the first 10 chars, it probably indicates that it is a long sentence without
    a start, and we don't want to remove it.

    Returns: Sentence without left trailing characters.
    """
    pattern = r'^.{0,10}?([A-ZŠČŘŽŠĎŤŇ])'
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

    # (?<=...) is a positive lookbehind assertion. It says: “Find a place preceded by the pattern inside the (?<=...), but don’t include it in the result.”
    # The pattern (?<=[.!?])\s+ matches any whitespace following a sentence-ending punctuation mark but keeps the punctuation as part of the previous sentence.
    sentences = nltk.sent_tokenize(concordance)
    for sentence in sentences:
        pattern = rf"\b{re.escape(target)}\b"
        match = re.search(pattern, sentence, flags=re.IGNORECASE)
        if match:
            return remove_left_trailing_chars(sentence)

    raise ValueError("Target word not found in concordance.")


def add_annotation_to_sentence(sentence: str, target:str, target_variants:list[str], is_target_valid:bool, is_from_corpora:bool) -> str:
    """
    Insert all information for the annotation into the sentence.
    If there are multiple variants of the target, one variant is chosen randomly.
    Args:
        sentence: sentence to be annotated
        target: a word or phrase which was mainly looked up in the corpora
        target_variants: other possible words or phrases which could occur at the same place as target in the sentence
        is_target_valid: whether the target is orthographically correct or not
        is_from_corpora: whether the sentence was extracted from the corpora as is or an error was added manually

    Example:
        input: "Stál před jejích chalupou.", "jejích", ["jejich"], False, False
        output: Stál před [*jejích|jejich|synthetic*] chalupou.


    Returns: Annotated sentence. The resulting format is:
    beginning_of_the_sentence[*error|valid|(synthetic or corpora)*]rest_of_the_sentence
    """
    target_variant = rd.choice(target_variants)

    if is_target_valid:
        if is_from_corpora:
            return sentence.replace(target, f"[*{target_variant}|{target}|corpora*]")
        else:
            return sentence.replace(target, f"[*{target_variant}|{target}|synthetic*]")

    else:
        if is_from_corpora:
            return sentence.replace(target, f"[*{target}|{target_variant}|corpora*]")
        else:
            return sentence.replace(target, f"[*{target}|{target_variant}|synthetic*]")
