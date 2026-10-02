# Q2 — Production-Ready Knowledge Base

This module implements the canonical business knowledge base for the Business Loan Qualification system.

## 1. Architecture Overview

```
[Raw Sources: Markdown, HTML, CSV, JSON, PDF]
                      │
                      ▼
        [DocumentLoader Pipeline]
                      │
                      ▼
     [TextCleaner & Deduplicator Engine]
 (Whitespace, Headings, Dates, Terminology, MinHash)
                      │
                      ▼
             [PIIScrubber Engine]
   (Masks Emails, Phones, Tax IDs, Accounts)
                      │
                      ▼
        [Semantic Header Chunker]
 (Preserves parent section headers & full attribution metadata)
                      │
                      ▼
   ┌──────────────────┴──────────────────┐
   ▼                                     ▼
[ChromaDB Vector Store]       [Rank-BM25 Sparse Index]
(gemini-embedding-001)           (Keyword Matching)
   └──────────────────┬──────────────────┘
                      ▼
      [Reciprocal Rank Fusion (RRF)]
                      │
                      ▼
      [Optional Cohere Reranker API]
                      │
                      ▼
  [Safe Fallback & Grounded Synthesis]
  (Gemini synthesis strictly from evidence)
```

---

## 2. Component Structure

- `data/raw/`: Raw source documents and `source_manifest.json`.
- `ingestion/loader.py`: Ingestion pipeline supporting `.md`, `.txt`, `.csv`, `.json`, `.html`, `.pdf`, `.docx`.
- `cleaning/cleaner.py`: Deterministic text cleaner, date normalizer, and duplicate/near-duplicate detector.
- `pii/pii_scrubber.py`: Regex-based PII scrubber for emails, phone numbers, tax IDs, and bank account details.
- `chunking/chunker.py`: Structure-aware semantic chunker preserving section headers and metadata.
- `indexing/index_manager.py`: ChromaDB dense index (using Google Gemini `gemini-embedding-001`) + BM25 sparse index.
- `reranking/reranker.py`: Optional Cohere reranker integration with safe fallback.
- `retrieval/retriever.py`: Hybrid retrieval engine with RRF fusion, fallback logic, and grounded Gemini synthesis.
- `citations/citation_generator.py`: Structured citation formatter.
- `api/app.py`: FastAPI REST API endpoints (`/kb/health`, `/kb/ingest`, `/kb/query`, `/kb/records/{id}`, `/kb/reindex`).
- `evaluation/`: Benchmark evaluation scripts and results.

---

## 3. Running Tests & Evaluation

```bash
# Run unit & integration test suite
pytest tests/test_q2_kb.py -v

# Run 5-query retrieval benchmark
python scripts/evaluate_retrieval.py
```
