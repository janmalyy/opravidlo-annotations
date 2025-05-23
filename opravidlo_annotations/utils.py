import json

from opravidlo_annotations.settings import FILES_DIR


def print_json(data: dict, indent: int = 4) -> None:
    """
    Print JSON data with nice indentation.

    Args:
        data (dict): The JSON data to print.
        indent (int, optional): Number of spaces for indentation. Defaults to 4.
    """
    print(json.dumps(data, ensure_ascii=False, indent=indent))


def concordances2text(filename: str, concordances: list[str]) -> None:
    """
    Write concordances to a file. If the file does not exist, it will be created.
    Args:
        filename: filename to write to. Only the unique name, the prefix "data_zajmena" and the filename extension will be added.
        concordances: lines to be written to the file
    Returns: None
    """
    full_filename = FILES_DIR / ("data_zajmena_" + filename + ".txt")
    do_append = True
    if not full_filename.exists():
        do_append = False
        print(f"File {full_filename} does not exist, creating a new one.")

    with open(full_filename, "a" if do_append else "w", encoding="utf-8") as f:
        for c in concordances:
            f.write(c + "\n")

    print(f"Succesfully wrote {len(concordances)} concordances to {full_filename}.")


def log_the_query(filename: str, corpora_name: str, query: str, number_of_concordances: int,
                  target: str, variants: list, is_target_valid: bool, is_from_corpora: bool) -> None:
    """
    Log the query into a JSON file. If the file does not exist, it will be created.
    The queries with the same filename are appended to the same file.
    Returns: Nothing.
    """
    full_filename = FILES_DIR / f"README_{filename}.json"

    if not full_filename.exists():
        starter = {"queries": []}
        with open(full_filename, "w", encoding="utf-8") as file:
            json.dump(starter, file, ensure_ascii=False, indent=4)
        print(f"File {full_filename} does not exist, creating a new one.")

    with open(full_filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    entry = {
        "query": query,
        "corpora_name": corpora_name,
        "number_of_concordances": number_of_concordances,
        "is_from_corpora": is_from_corpora,
    }

    if is_target_valid:
        entry["correct"] = [target]
        entry["error"] = variants
    else:
        entry["correct"] = variants
        entry["error"] = [target]

    data["queries"].append(entry)

    with open(full_filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)