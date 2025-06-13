# Absolutely Cosmetic Knowledge Base Pipeline

This repository contains the data pipeline and API for building a multi-modal knowledge base for Absolutely Cosmetic, powering a Vapi voice AI agent.

## Overview

We have scraped and processed two types of knowledge from the Absolutely Cosmetic website:

- **Treatments**: All treatment pages were scraped and ingested into a graph database (Graphiti).
- **Concerns**: All concern pages were scraped, combined, and used as a vector database knowledge base.

Both knowledge bases are available to a Vapi voice AI agent for rich, context-aware conversational experiences.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials. This file contains the required environment variables for Neo4j and OpenAI API keys used throughout the project.

---

## Data Collection & Processing

### 1. Scraping with Firecrawl
- We used the JSON extraction mode of [Firecrawl](https://firecrawl.dev/) to scrape both treatments and concerns from the Absolutely Cosmetic website.
- The scraping scripts are provided in the repository:
  - `scraper.py` and related scripts for treatments
  - `concerns_scraper.py` for concerns

### 2. Concerns Knowledge Base (Vector DB)
- All concern JSON files were combined using `combine_concerns_to_md.py`.
- The combined markdown is used as a vector database knowledge base for the Vapi voice AI agent.
- This enables semantic search and retrieval for user queries about cosmetic concerns.

### 3. Treatments Knowledge Base (Graph DB)
- All treatment JSON files were ingested into [Graphiti](https://github.com/getzep/graphiti) using `graph_ingestion_entity.py`.
- This creates a temporal, entity-rich knowledge graph of all treatments, their properties, and relationships.
- The graph knowledge base supports advanced graph and semantic queries.

---

## API: FastAPI Graphiti Endpoint

- The graph knowledge base is exposed as a FastAPI API in `app.py`.
- The API provides endpoints for hybrid semantic/graph search over the treatments knowledge base.
- The Vapi voice AI agent queries this API to answer user questions about treatments, procedures, and their relationships.

---

## Project Structure

- `docs_kb/` — Scraped treatment JSON files
- `docs_concerns_kb/` — Scraped concern JSON files
- `combine_concerns_to_md.py` — Script to combine concerns into a markdown/vector DB
- `graph_ingestion_entity.py` — Script to ingest treatments into Graphiti
- `app.py` — FastAPI app exposing the graph knowledge base
- `README.md` — This file
- `.env.example` — Example environment variable file

---

## How to Use

1. **Copy Environment Variables**: Copy `.env.example` to `.env` and fill in your credentials.
2. **Scrape Data**: Use the provided scraper scripts to extract JSON from the Absolutely Cosmetic website.
3. **Combine Concerns**: Run `python combine_concerns_to_md.py` to generate the vector DB markdown.
4. **Ingest Treatments**: Run `python graph_ingestion_entity.py` to populate the Graphiti graph database.
5. **Start API**: Run `uvicorn app:app --reload` to start the FastAPI server.
6. **Integrate with Vapi**: Point your Vapi voice AI agent to the FastAPI endpoint for graph-based queries, and to the vector DB for concern-based queries.

---

## About Absolutely Cosmetic

Absolutely Cosmetic is a leading provider of cosmetic treatments and procedures. This project enables advanced, AI-powered conversational access to the clinic's expertise, leveraging both vector and graph knowledge bases for best-in-class user experience. 