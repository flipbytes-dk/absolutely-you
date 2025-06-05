# Absolutely You: Procedure Markdown Generator

This project provides a Python script to extract structured cosmetic procedure data from JSON files and combine them into a single, human-readable markdown file.

## Project Description

- **Purpose:** Aggregate structured data about cosmetic procedures (scraped from the web) into a single markdown document for easy review, sharing, or further processing.
- **Input:** Individual JSON files (not included in this repo) in a `docs_kb/` directory, each containing a `json` field with procedure details.
- **Output:** A single `procedures.md` file in the project root, with each procedure formatted as a markdown section.

## Data Pipeline Overview

### 1. Scraping Structured Data from the Web

- **Tool:** [Firecrawl Python SDK](https://github.com/firecrawl/firecrawl-python)
- **Schema:** A Pydantic schema (`ExtractSchema`) defines the fields to extract (procedure_name, explanation, treatment_overview, procedure_type, cost, recovery_time, results_duration, miscellaneous_information).
- **Process:**
  - Crawl the target website for procedure URLs using `app.map_url()`.
  - For each URL, extract structured data using `app.scrape_url()` with the schema and save the result as a JSON file in `docs_kb/`.
  - All discovered links are saved to `all_links.json` for inspection.
  - Non-serializable fields are filtered out for robust JSON output.

### 2. Generating a Combined Markdown File

- **Script:** `generate_procedures_md.py`
- **Function:** Reads all `.json` files in `docs_kb/`, extracts the `json` field, and writes a combined, well-formatted `procedures.md` file.
- **Format:** Each procedure is a top-level heading with subheadings for each field and includes the source URL as metadata.

### 3. Ingesting Data into Graphiti/Neo4j

- **Script:** `ingest_to_graphiti.py` (not included in the repo by default, but referenced for workflow)
- **Setup:**
  - Requires environment variables for Neo4j connection (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`).
  - Uses the `graphiti-core` Python SDK.
- **Process:**
  - Iterates over the JSON files, extracting the `json` field for each procedure.
  - Each procedure is ingested as an "episode" in Graphiti, with robust error handling (skipping files with missing/invalid data, logging errors, and continuing processing).
  - Metadata and grouping are handled as required by the Graphiti data model.

> **Note:** The Jupyter notebook `ingest_to_graphiti.ipynb` is not part of the repo or the recommended workflow. Use the standalone script for ingestion.

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