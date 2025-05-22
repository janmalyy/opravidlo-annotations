import re

def correct_punctuation(text: str) -> str:
    """
    Corrects punctuation in a string. It removes any trailing whitespaces before the punctuation mark.
    """
    return re.sub(r"\s+([.,?!:;])", r"\1", text)