import os

from opravidlo_annotations.settings import FILES_DIR

def concordances2text(filename: str, concordances: list[str], do_append: bool=True) -> None:
    """
    Write concordances to a file.
    Args:
        filename: filename to write to. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
        concordances: lines to be written to the file
        do_append: whether to append to the file or write a new one (or overwrite)

    Returns: None
    """
    full_filename = FILES_DIR / ("data_zajmena_" + filename + ".txt")
    if do_append and full_filename not in os.listdir(FILES_DIR):
        do_append = False
        print(f"File {full_filename} does not exist, creating a new one.")

    with open(full_filename, "a" if do_append else "w", encoding="utf-8") as f:
        for c in concordances:
            f.write(c + "\n")

    print(f"Succesfully wrote {len(concordances)} concordances to {full_filename}.")