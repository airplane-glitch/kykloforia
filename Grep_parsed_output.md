# Filtering Parsed FAA SWIM Data with `grep`

This guide explains how to use the `grep` command to filter structured output from the `parce9.py` parser after validating that the data quality is acceptable.

---

## Step 1: Run the Parser

Use `parce9.py` to convert raw FAA `.log` files into a structured format:

- `parsed_output.txt` contains valid rows
- `bad_data.txt` contains rows missing critical fields

These files are saved via interactive file selectors (GUI) when you run the script.

---

## Step 2: Check for Bad Data

Before filtering, **review the `bad_data.txt`** file to ensure data quality is acceptable.

If the number of ignored rows is high, consider reviewing the log source or improving the field parsing.

## Step 3: Filter by Message Type (DAB / F11)

Once you've confirmed the data is reliable, filter it into type-specific files using grep:

- ` grep '^DAB,' parsed_output.txt > dab_filtered.txt`
- ` grep ^F11,' parsed_output.txt > F11_filtered.txt`

This creates two separate datasets, each with records from one primary partition.

Note:
If your input file (parsed_output.txt) or desired output filenames are different, make sure to update the commands accordingly. For example:

- ` grep '^Primary_Partition,' my_parsed_file.txt > dab_subset.txt `

## Step 4: Preview the Data

To check the structure and sample contents:

- ` head -n 10 dab_filtered.txt `
- ` tail -n 10 F11_filtered.txt `

If the data looks good, it's ready for use with OpenARIA or any downstream analysis.

## Step 5: Follow the instructions on OpenARIA to detect events.