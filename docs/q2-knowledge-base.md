# Question 2 — Production-Ready Knowledge Base Architecture

## 1. Executive Summary

Question 2 provides the canonical Knowledge Base for the Business Loan Qualification system. All facts, product limits, interest rates, eligibility criteria, and objection handling scripts reside strictly in Q2.

The system uses **Google Gemini Embeddings (`gemini-embedding-001`)** for dense vector search and **`rank_bm25`** for sparse keyword search, combined via **Reciprocal Rank Fusion (RRF)**.

---

## 2. Pipeline Stage Breakdown

### 1. Ingestion (`q2_knowledge_base/ingestion/loader.py`)
- Ingests raw source documents across multiple formats (`.md`, `.txt`, `.csv`, `.json`, `.html`, `.pdf`).
- Retains full metadata attribution (`source_id`, `source_name`, `source_type`, `version`, `category`, `ingestion_timestamp`, `original_location`).

### 2. Cleaning & Deduplication (`q2_knowledge_base/cleaning/cleaner.py`)
- Normalizes whitespace, heading tags (`#`), dates (`YYYY-MM-DD`), and financial terms (`turnover` -> `revenue (turnover)`).
- Detects exact duplicates via MD5 hashing and near-duplicates via Jaccard token set similarity (threshold > 0.75).

### 3. PII Detection & Redaction (`q2_knowledge_base/pii/pii_scrubber.py`)
- Redacts emails (`[REDACTED_EMAIL]`), phone numbers (`[REDACTED_PHONE]`), tax IDs/SSNs (`[REDACTED_TAX_ID]`), bank accounts (`[REDACTED_ACCOUNT]`), and street addresses.
- Sets `pii_flag=True` on affected chunks.

### 4. Structure-Aware Chunking (`q2_knowledge_base/chunking/chunker.py`)
- Splits documents by Markdown headers (`#`, `##`) or HTML heading tags (`<h1>`, `<h2>`), preserving section context.
- Attaches metadata to every chunk: `record_id`, `chunk_id`, `title`, `category`, `source_id`, `source_name`, `source_type`, `version`, `section`, `content`, `created_at`, `pii_flag`.

### 5. Hybrid Indexing & Retrieval (`q2_knowledge_base/indexing/`, `q2_knowledge_base/retrieval/`)
- **Dense Vector Store**: Persistent ChromaDB using `gemini-embedding-001` (3072 dimensions).
- **Sparse Search**: `BM25Okapi` sparse keyword search.
- **Fusion**: Reciprocal Rank Fusion (RRF):
  $$RRF\_Score(chunk) = \frac{1}{60 + rank_{vector}} + \frac{1}{60 + rank_{bm25}}$$

### 6. Optional Reranking (`q2_knowledge_base/reranking/reranker.py`)
- Integrates Cohere Rerank API if `COHERE_API_KEY` is present. Falls back gracefully to RRF rankings if absent or offline.

### 7. Safe Fallback & Grounded Synthesis (`q2_knowledge_base/citations/`)
- If max retrieval score is below threshold, returns:
  `"I don't have enough verified information in the knowledge base to answer that reliably. I can connect you with a human representative."`
- Otherwise, Gemini generates a grounded response strictly from retrieved chunks, appending traceable citations.

---

## 3. FastAPI REST API Endpoints

- `GET /kb/health`: Returns API status, loaded chunk count, and index health.
- `POST /kb/ingest`: Triggers raw document ingestion and indexing pipeline.
- `POST /kb/query`: Accepts `{"query": "...", "top_k": 5}` and returns grounded answer + citations.
- `GET /kb/records/{record_id}`: Retrieves specific chunk metadata by record ID.
- `POST /kb/reindex`: Re-runs pipeline and updates vector + BM25 indexes.

---

## 4. Empirical Evaluation Results

Evaluated 5 benchmark queries in `scripts/evaluate_retrieval.py`:
- **Product Question**: 100% Match (Score: 0.9996)
- **Qualification Question**: 100% Match (Score: 0.9959)
- **Policy Question**: 100% Match (Score: 0.9846)
- **FAQ Question**: 100% Match (Score: 0.9982)
- **Objection Question**: 100% Match (Score: 0.9955)

**Overall Accuracy**: **100% (5/5 Correct)**
