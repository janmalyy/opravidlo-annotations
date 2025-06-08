import json
from pathlib import Path

from opravidlo_annotations.settings import FILES_DIR


def log_the_query(filename: str, corpus_name: str, query: str, number_of_concordances: int,
                  target: str, variants: list, is_target_valid: bool) -> None:
    """
    Log the query into a JSON file. If the file does not exist, it will be created.
    The queries with the same filename are appended to the same file.
    Returns: Nothing.
    """
    full_filename = FILES_DIR / f"README_{filename}.json"

    if not full_filename.exists():
        starter = {"queries": [], "comments": []}
        with open(full_filename, "w", encoding="utf-8") as file:
            json.dump(starter, file, ensure_ascii=False, indent=4)
        print(f"File {full_filename} does not exist, creating a new one.")

    with open(full_filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    looking_for = "correct" if is_target_valid else "error"
    entry = {
        "query": query,
        "corpus_name": corpus_name,
        "number_of_concordances": number_of_concordances,
        "is_looking_for": looking_for,
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


def generate_query_summary(data: dict) -> list:
    """
    Generate a query summary from JSON data, merging same queries across corpora,
    and adjusting column widths based on content length.

    Args:
        data (dict): JSON data containing query logs.

    Returns:
        list: Lines of formatted summary as strings.
    """
    from collections import defaultdict

    # Merge by query text
    merged = defaultdict(lambda: {"corpora": [], "correct": set(), "error": set(), "targets": set()})

    for entry in data.get("queries", []):
        query = entry.get("query", "").replace("\n", " ").strip()
        corpus = entry.get("corpus_name") or entry.get("corpora_name") or "N/A"
        hits = entry.get("number_of_concordances", 0)
        correct = entry.get("correct", [])
        error = entry.get("error", [])
        target = entry.get("is_looking_for", "N/A")

        merged[query]["corpora"].append((corpus, hits))
        merged[query]["correct"].update(correct)
        merged[query]["error"].update(error)
        merged[query]["targets"].add(target)

    # Prepare data rows
    rows = []
    for query, details in merged.items():
        # Sort corpora by hits descending
        corpora_sorted = sorted(details["corpora"], key=lambda x: -x[1])
        corpora_str = ", ".join(f"{c[0]} ({c[1]})" for c in corpora_sorted)

        correct = ", ".join(sorted(details["correct"])) if details["correct"] else "N/A"
        errors = ", ".join(sorted(details["error"])) if details["error"] else "N/A"
        targets = ", ".join(sorted(details["targets"])) if details["targets"] else "N/A"

        rows.append([query, corpora_str, f"*{correct}*", f"*{errors}*", targets])

    # Determine column widths
    headers = ["Query", "Corpora (Hits)", "Correct Form", "Frequent Errors", "Target Type"]
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(item))

    # Create header and separator
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    separator = "|-" + "-|-".join("-" * col_widths[i] for i in range(len(headers))) + "-|"

    # Prepare summary
    summary = [header_line, separator]
    for row in rows:
        line = "| " + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
        summary.append(line)

    return summary


def generate_text_readme(filename: Path) -> None:
    """
    Generate a text readme file from JSON readme file.
    Args:
        filename (Path): Path to JSON readme file

    Returns: None. It saves the generated text readme file into FILES_DIR.
    """
    with open(FILES_DIR / filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    comments = data["comments"]
    summary_lines = generate_query_summary(data)

    txt_filename = filename.with_suffix(".txt")
    with open(FILES_DIR / txt_filename, "w", encoding="utf-8") as file:
        [file.write(comment+"\n") for comment in comments]
        file.write("\n")
        [file.write(summary_line+"\n") for summary_line in summary_lines]

        print(f"Summary successfully written to {txt_filename}.")
