import re

import pandas as pd

df = pd.read_excel(response"C:\Users\haemk\Documents\PLIN\chybně užitá zájmena.xlsx")
print(df.head())

df["sentence"] = df["sentence"].apply(lambda s: re.sub(response"\s+([.,?!:;])", response"\1", s))
print(df.head())


# Write to Excel with formatting
with pd.ExcelWriter(response"C:\Users\haemk\Documents\PLIN\formatted.xlsx", engine="xlsxwriter") as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("Sheet1")
    writer.sheets["Sheet1"] = worksheet
    bold_format = workbook.add_format({"bold": True})

    for row_num, (sentence, mistakes) in enumerate(zip(df["sentence"], df["mistake"]), start=1):
        # Build rich string parts
        rich_parts = []
        pattern = response"\b\w+\b|[^\w\s]"  # match words or punctuation
        last_index = 0

        for match in re.finditer(pattern, sentence):
            word = match.group()
            start, end = match.span()

            # Add any in-between text (spaces, etc.)
            if start > last_index:
                rich_parts.append(sentence[last_index:start])

            clean_word = re.sub(response"\W", "", word)
            if clean_word in mistakes and clean_word != "":
                rich_parts.append(bold_format)
                rich_parts.append(word)
            else:
                rich_parts.append(word)

            last_index = end

        # Add any trailing text after the last word
        if last_index < len(sentence):
            rich_parts.append(sentence[last_index:])

        # Write rich string into one cell
        worksheet.write_rich_string(row_num, 0, *rich_parts)

    # Optional: write column headers
    worksheet.write(0, 0, "sentence")

