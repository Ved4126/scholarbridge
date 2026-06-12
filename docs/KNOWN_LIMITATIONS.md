# Known Limitations

This document explicitly outlines features that are **not** present in the current MVP. This repository accurately represents the current codebase limitations.

## Storage and Infrastructure
- **In-Memory Storage:** All profile storage (`database.py`) and scoring cache (`_score_cache`) use standard Python dictionaries. 
- **Data Volatility:** Data is completely lost every time the FastAPI server restarts.
- **No Real Database:** There is no database persistence (no PostgreSQL, MongoDB, or SQLite).
- **Single-Process Assumption:** The cache mechanisms assume a single worker. Deploying with multiple workers (e.g. via Gunicorn) will lead to split, inconsistent states.

## Product Features
- **No Authentication / Authorization:** All endpoints are completely open. Anyone can read, modify, or delete any profile given its UUID.
- **No Frontend:** This repository contains only the backend API logic.
- **No Payment System:** Billing and subscription logic do not exist.

## Data and AI
- **Mock/Test Data Only:** The system does not possess a real, exhaustive scholarship corpus. It operates entirely on developer test/dev data locally stored in the `data/` directory.
- **No Scraping:** There is no active scholarship scraper agent or live updating mechanism.
- **No Vector Search:** There is no RAG, semantic similarity search, or vector database (e.g., Pinecone, Weaviate).
- **No ML Ranking:** The scoring engine is a purely deterministic, rules-based engine. There is no LightGBM, neural networks, or active machine learning implemented.
- **No RLHF:** Reinforcement Learning from Human Feedback is not implemented.

## Disclaimers
The recommendations provided by this application are mathematical approximations based on given heuristics. This software does **not** provide legal, immigration, or financial advice.
