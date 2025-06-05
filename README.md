# Absolutely You: Procedure Markdown Generator

This project provides a Python script to extract structured cosmetic procedure data from JSON files and combine them into a single, human-readable markdown file.

## Project Description

- **Purpose:** Aggregate structured data about cosmetic procedures (scraped from the web) into a single markdown document for easy review, sharing, or further processing.
- **Input:** Individual JSON files (not included in this repo) in a `docs_kb/` directory, each containing a `json` field with procedure details.
- **Output:** A single `procedures.md` file in the project root, with each procedure formatted as a markdown section.

## Usage

1. Place your JSON files in a `docs_kb/` directory (excluded from this repo).
2. Run the script:

```bash
python generate_procedures_md.py
```

3. The script will create or overwrite `procedures.md` in the project root.

## Requirements

- Python 3.7+
- No external dependencies (uses only the Python standard library)

## Notes

- The script ignores `docs_kb/`, `venv/`, `.env`, and other sensitive or unnecessary files.
- Do **not** commit scraped data or secrets to this repository.

## License

[Apache 2.0](LICENSE) 