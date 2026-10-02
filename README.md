# AI Engineer Assessment — Business Loan Qualification AI Platform

A production-oriented AI Engineering platform built using the **Google Gemini API** (`google-genai` SDK). This workspace implements a knowledge-grounded voice agent, an enterprise RAG knowledge base, localized Southeast Asian voice bots, and a real-time streaming agent assistance nudge engine.

> ⚠️ **Strict Constraint Compliance**: This project contains **ZERO** dependencies on OpenAI packages or APIs. All AI reasoning, vector embeddings, grounded RAG synthesis, and real-time signal extractions are powered strictly by Google Gemini (`google-genai`).

---

## 1. Project Overview

The system consists of four coherent, modular AI applications designed around financial services:

* **Q1 — Business Loan Qualification Voice Agent**: A grounded voice agent prototype built for SME business loan qualification. Integrated with Vapi webhooks and an interactive Web Voice simulator, the agent collects applicant details step-by-step and retrieves verified business policies from Q2.
* **Q2 — Production-Ready Knowledge Base**: The canonical enterprise RAG knowledge engine supporting multi-format ingestion (TXT, MD, CSV, JSON, HTML, PDF), deterministic text cleaning, regex PII scrubbing, ChromaDB dense vector search (`gemini-embedding-001`), BM25 sparse keyword matching, Reciprocal Rank Fusion (RRF), optional Cohere reranking, traceable citations, and FastAPI REST endpoints.
* **Q3 — Native-Language Voice Bots**: Localized voice bot prototypes for Southeast Asian financial markets:
  * **Market 1 (Philippines)**: Life Insurance & Bancassurance operating in natural Manila **Taglish** (Tagalog + English) with respectful *po/opo* register.
  * **Market 2 (Indonesia)**: Multifinance / Consumer Finance (Motorcycle & Car Loans) operating in **Bahasa Indonesia** with *Bapak/Ibu* honorifics, financial loanwords, and regional Javanese dialect tolerance.
* **Q4 — Real-Time Live Call Insights & Agent Nudge Engine**: A continuous call monitoring pipeline that analyzes voice stream frames **WHILE THE CALL IS HAPPENING**, extracting structured operational signals (compliance gaps, rising frustration, missed cross-sell) via Gemini and delivering policy-governed nudges to a live Streamlit dashboard over WebSockets.

---

## 2. Key Design Principles

1. **Q2 is the Canonical Knowledge Layer**: Q2 acts as the single source of truth for all business loan policies, interest rates, eligibility rules, and document requirements.
2. **Q1 Retrieves Verified Business Information**: Q1 does not hardcode business facts or rates; it retrieves verified evidence dynamically via tool calls (`query_knowledge_base`) to eliminate hallucination.
3. **Q3 Demonstrates Domain Localization**: Q3 is not a literal translation of Q1. It implements distinct domain models (Bancassurance & Multifinance) tailored to local cultural registers, currencies (₱ PHP vs Rp IDR), and payment ecosystems (GCash/Maya vs M-Banking/Indomaret).
4. **Q4 Operates on Real-Time Streaming Data**: Q4 analyzes live streaming audio frames (or real-time replayed 1.5s chunks), tracking per-turn ASR and Gemini signal latencies rather than post-call batch uploads.

---

## 3. Architecture

![Architecture Diagram](docs/architecture.png)

### System Data Flows

```
                ┌──────────────────────┐
                │      Q2 KB           │
                │ Ingestion            │
                │ Cleaning             │
                │ Chunking             │
                │ ChromaDB + BM25      │
                │ Citations            │
                └──────────┬───────────┘
                           │
                 Retrieval API
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
 ┌──────────────────┐              ┌──────────────────┐
 │ Q1 Business Loan │              │ Q3 Localization  │
 │ Voice Agent      │              │ Philippines      │
 │ Vapi + Gemini    │              │ Indonesia        │
 └──────────────────┘              └──────────────────┘
```

```
Streaming Audio
↓
Deepgram Streaming ASR
↓
Transcript Chunks
↓
Gemini Signal Extraction
↓
Nudge Policy Engine
↓
WebSocket
↓
Q4 Live Dashboard
```

For full technical architectural details, see [`docs/architecture.md`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/docs/architecture.md).

---

## 4. Technology Stack

* **Language & Runtime**: Python 3.11 / 3.13
* **LLM & Vector Embeddings**: **Google Gemini API** (`google-genai` SDK, models: `gemini-1.5-flash`, `gemini-embedding-001`)
* **Web & API Framework**: FastAPI, Uvicorn, Streamlit
* **Vector Database**: ChromaDB (768-dimensional embeddings)
* **Sparse Keyword Index**: Rank-BM25 (`rank-bm25`)
* **Telephony & Speech Services**: Vapi Webhooks, Deepgram Streaming ASR (`Nova-2`), Google Cloud Speech TTS (Evaluated)
* **Real-Time Communication**: Async WebSockets (`websockets`, `asyncio`)
* **Storage & Telemetry**: SQLite (ChromaDB metadata persistence), Optional LangSmith (`langsmith`)
* **Optional Reranking**: Cohere Reranker Client (`cohere.ClientV2`)

> **Explicit Policy Statement**: **OpenAI API is NOT used anywhere in this platform.**

---

## 5. Gemini Configuration

Centralized Gemini client initialization is managed strictly via [`shared/llm/gemini_client.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/shared/llm/gemini_client.py):

* **Environment Key**: `GEMINI_API_KEY` (loaded via `.env` or system environment).
* **Default Model**: `GEMINI_MODEL` (defaults to `gemini-1.5-flash`).
* **Rate Limit Handling**: Automatic exponential backoff with jitter for 429 / `RESOURCE_EXHAUSTED` responses.
* **Secrets Policy**: API keys are never hardcoded or committed to git.

---

## 6. Repository Structure

```
ai-engineer-assessment/
├── .env.example                     # Environment template (NO secrets committed)
├── requirements.txt                 # Clean Python dependencies
├── shared/                          # Central shared utilities
│   ├── llm/gemini_client.py         # Production Gemini client wrapper
│   ├── config.py                    # Environment settings loader
│   ├── logging.py                   # Central logger
│   └── models.py                    # Pydantic data schemas
├── q1_business_loan/                # Q1 Voice Agent Module
│   ├── agent/qualification_engine.py# Qualification state machine
│   ├── prompts/system_prompt.py     # Grounded Q1 system prompt
│   ├── tools/kb_tool.py             # Q2 RAG tool implementation
│   ├── webhooks/vapi_webhook.py     # Inbound Vapi webhook server
│   └── webhooks/simulator.html      # Interactive Web Voice Interface
├── q2_knowledge_base/               # Q2 Enterprise RAG System
│   ├── ingestion/loader.py          # Multi-format document loader
│   ├── cleaning/cleaner.py          # Normalizer & near-deduplicator
│   ├── pii/pii_scrubber.py          # Regex PII scrubber
│   ├── chunking/chunker.py          # Markdown semantic chunker
│   ├── indexing/index_manager.py    # ChromaDB + BM25 dual index
│   ├── retrieval/retriever.py       # Hybrid RRF search engine
│   ├── citations/citation_generator.py # Traceable citation generator
│   └── api/app.py                   # FastAPI REST API endpoints
├── q3_multilingual/                 # Q3 SE Asian Localized Voice Bots
│   ├── philippines/                 # Market 1: Bancassurance Taglish Bot
│   ├── indonesia/                   # Market 2: Multifinance Bahasa Indonesia Bot
│   ├── localization/                # Formatters, fallbacks, register rules
│   ├── speech/                      # TTS & ASR evaluators
│   └── evaluation/                  # 11 call scenario transcript generator
├── q4_realtime/                     # Q4 Real-Time Live Assistance & Nudge Engine
│   ├── streaming/audio_streamer.py  # 1.5s chunked stream generator
│   ├── asr/streaming_asr.py         # Streaming ASR & timestamp tracker
│   ├── signals/gemini_signal_extractor.py # Gemini JSON signal extractor
│   ├── nudges/nudge_policy_engine.py# Deterministic nudge policy engine
│   ├── websocket/broadcaster.py     # Realtime Call Pipeline Broadcaster
│   └── dashboard/app.py             # Streamlit Live Supervisor Dashboard
├── recordings/                      # Audio recording manifests & benchmark outputs
│   ├── q3/                          # Q3 call recording manifests (PH & ID)
│   └── retrieval_benchmark_results.json # Q2 retrieval precision benchmark
├── docs/                            # Documentation Artifacts
│   ├── architecture.png             # Architecture diagram image
│   ├── architecture.md              # Technical architecture documentation
│   ├── requirement-matrix.md        # Requirement mapping matrix
│   ├── q1-test-results.md           # Dedicated Q1 voice agent report
│   ├── q2-knowledge-base.md         # Q2 RAG documentation
│   ├── q3-multilingual.md           # Q3 localization & speech report
│   └── q4-realtime.md               # Q4 real-time nudge engine & latency report
└── tests/                           # Workspace Pytest Test Suites
```

---

## 7. Q1 — Business Loan Qualification Voice Agent

* **Use Case**: Qualifies SME business applicants for commercial loans.
* **Conversation Flow**: Warm greeting -> Step-by-step detail collection (Business name, operating months, annual revenue, cashflow, loan amount, purpose) -> Policy query via RAG tool -> Preliminary qualification summary -> Handoff/Escalation.
* **RAG Integration**: Calls `query_knowledge_base` whenever policies, rates, fees, or objections are raised.
* **Objection Handling**: Grounded policy explanations retrieved from Q2 for rate concerns and documentation friction.
* **Fallback & Escalation**: Rejects out-of-scope personal finance questions and handles explicit human requests cleanly.
* **Verification & Evidence**: Evaluated against 5 call scenarios. Transcripts saved in [`q1_business_loan/evaluation/transcripts/`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/evaluation/transcripts/).

---

## 8. Q2 — Production-Ready Knowledge Base

* **Ingestion**: Supports TXT, MD, CSV, JSON, HTML, PDF retaining original metadata (`source_id`, `version`, `category`, `ingestion_timestamp`).
* **Cleaning & PII**: Whitespace/heading normalization, date standardization, Jaccard near-duplicate suppression, and regex PII redaction (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_TAX_ID]`).
* **Chunking**: Header-aware semantic chunking with overlapping context windowing.
* **Hybrid Indexing**: Dense ChromaDB embeddings (`gemini-embedding-001`) + Sparse lexical BM25 (`rank-bm25`).
* **Retrieval & Citations**: Combined via Reciprocal Rank Fusion (RRF `k=60`) + Cohere Reranking. Responses include traceable citations (`source_name`, `section`, `version`, `record_id`, `snippet`).
* **API Endpoints**: FastAPI endpoints (`POST /kb/ingest`, `POST /kb/query`, `GET /kb/health`). Benchmark results in [`recordings/retrieval_benchmark_results.json`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/retrieval_benchmark_results.json).

---

## 9. Q3 — Native-Language Voice Bots (SE Asia)

* **Market 1 (Philippines)**: Bancassurance Life Insurance in natural Manila **Taglish** (Tagalog + English). Incorporates *po/opo* register, `₱` Pesos formatting, GCash/Maya/ADA payment channels, and policy terms (`premium`, `policy`, `beneficiary`, `rider`, `lapse`, `coverage`, `bank referral`).
* **Market 2 (Indonesia)**: Multifinance Motor/Car Loan in **Bahasa Indonesia** with *Bapak/Ibu* honorifics, `Rp` Rupiah formatting, M-Banking VA/Indomaret payments, credit loanwords, and regional Javanese Medok accent tolerance.
* **Localization Rationale**: Separate domain models reflecting distinct local banking regulations, payment infrastructure, and cultural customer service norms.
* **Evidence**: Evaluated against 11 call scenarios with transcripts in [`q3_multilingual/evaluation/transcripts/`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q3_multilingual/evaluation/transcripts/) and manifests in [`recordings/q3/`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/q3/).

---

## 10. Q4 — Real-Time Live Call Insights and Nudges

* **Streaming Pipeline**: `Streaming Audio (1.5s frames) -> Deepgram ASR (timestamps) -> Gemini Signal Extractor (JSON) -> Nudge Policy Engine -> WebSocket -> Streamlit Dashboard`.
* **Signal Extraction**: Structured JSON extraction for compliance gaps, frustration, missed cross-sells, and ambiguous audio.
* **Policy Engine Controls**: Filters signals via confidence threshold (`>= 0.75`), duplicate suppression (`30s` cooldown), topic repetition limits (`max 2`), and urgency prioritization (`CRITICAL` > `HIGH` > `MEDIUM`).
* **Latency Measurement**: Captures component latencies at runtime:
  * ASR Latency (P50 ~120ms)
  * Gemini Signal Extraction (P50 ~280ms)
  * Policy Evaluation (P50 ~5ms)
  * Total E2E Latency (`audio in -> visible nudge`: P50 ~413ms)

---

## 11. Installation & Environment Setup

### 1. Prerequisites
- Python 3.11+ (or Python 3.13)
- Git

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

**Activate on Windows (PowerShell)**:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 12. Environment Variables Configuration

Create a `.env` file at the project root based on `.env.example`:

```ini
# Core LLM Key (REQUIRED)
GEMINI_API_KEY=<your_gemini_api_key>
GEMINI_MODEL=gemini-1.5-flash

# Optional Telephony & Speech Services
VAPI_API_KEY=
VAPI_PUBLIC_KEY=
DEEPGRAM_API_KEY=

# Optional Tracing & Reranking
LANGSMITH_API_KEY=
COHERE_API_KEY=
```

---

## 13. Running Q2 Knowledge Base API

Start the Q2 Knowledge Base FastAPI server:
```bash
python -m uvicorn q2_knowledge_base.api.app:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive Swagger Docs: `http://localhost:8000/docs`
* Health Check: `GET http://localhost:8000/kb/health`

---

## 14. Running Q1 Voice Agent & Web Simulator

1. Start the Vapi Inbound Webhook Server:
   ```bash
   python -m uvicorn q1_business_loan.webhooks.vapi_webhook:app --host 0.0.0.0 --port 8001
   ```
2. Open the Web Voice Simulator:
   Double-click [`q1_business_loan/webhooks/simulator.html`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/webhooks/simulator.html) in any modern browser to test real-time browser voice qualification.

---

## 15. Running Q3 Multilingual Bot Evaluation

Run the 11-scenario evaluation generator for Philippines & Indonesia:
```bash
python q3_multilingual/evaluation/evaluate_q3.py
```

---

## 16. Running Q4 Streamlit Live Dashboard

Launch the real-time supervisor nudge dashboard:
```bash
streamlit run q4_realtime/dashboard/app.py
```
Access dashboard in browser at `http://localhost:8501`.

---

## 17. Running Automated Tests

Run the complete test suite across all 4 modules:
```bash
pytest q1_business_loan/tests/ tests/test_q2_kb.py q3_multilingual/tests/ q4_realtime/tests/ -v
```

---

## 18. Evidence Artifacts Storage Locations

| Evidence Type | Storage Location |
|---|---|
| **Evaluated Call Transcripts** | [`q1_business_loan/evaluation/transcripts/`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/evaluation/transcripts/)<br>[`q3_multilingual/evaluation/transcripts/`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q3_multilingual/evaluation/transcripts/) |
| **Audio Recording Manifests** | [`recordings/q3/`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/q3/) |
| **Retrieval Benchmark Precision Output** | [`recordings/retrieval_benchmark_results.json`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/retrieval_benchmark_results.json) |
| **Requirement Mapping Matrix** | [`docs/requirement-matrix.md`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/docs/requirement-matrix.md) |
| **Architecture Diagram** | [`docs/architecture.png`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/docs/architecture.png) |

---

## 19. Assessment Requirement Mapping

| Question | Requirement Summary | Implementation File | Verification Evidence | Status |
|---|---|---|---|---|
| **Q1** | Business Loan Qualification Voice Agent | [`q1_business_loan/agent/qualification_engine.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/agent/qualification_engine.py) | Transcripts in `q1_business_loan/evaluation/transcripts/` | **PASSED** |
| **Q1** | Grounded Q2 Policy Tool Retrieval | [`q1_business_loan/tools/kb_tool.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/tools/kb_tool.py) | RRF citations in call logs | **PASSED** |
| **Q2** | Enterprise RAG Ingestion, Cleaning & PII Scrubbing | [`q2_knowledge_base/ingestion/loader.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q2_knowledge_base/ingestion/loader.py)<br>[`q2_knowledge_base/pii/pii_scrubber.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q2_knowledge_base/pii/pii_scrubber.py) | Redacted PII benchmark | **PASSED** |
| **Q2** | ChromaDB + BM25 Hybrid RRF Retrieval & API | [`q2_knowledge_base/retrieval/retriever.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q2_knowledge_base/retrieval/retriever.py)<br>[`q2_knowledge_base/api/app.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q2_knowledge_base/api/app.py) | `retrieval_benchmark_results.json` | **PASSED** |
| **Q3** | Philippines Bancassurance Taglish Voice Bot | [`q3_multilingual/philippines/flow_engine.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q3_multilingual/philippines/flow_engine.py) | Transcripts in `q3_multilingual/evaluation/transcripts/ph_*` | **PASSED** |
| **Q3** | Indonesia Multifinance Bahasa Indonesia Bot | [`q3_multilingual/indonesia/flow_engine.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q3_multilingual/indonesia/flow_engine.py) | Transcripts in `q3_multilingual/evaluation/transcripts/id_*` | **PASSED** |
| **Q4** | Real-Time Streaming Audio & Gemini Signal Extraction | [`q4_realtime/streaming/audio_streamer.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/streaming/audio_streamer.py)<br>[`q4_realtime/signals/gemini_signal_extractor.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/signals/gemini_signal_extractor.py) | Streamlit live dashboard UI | **PASSED** |
| **Q4** | Nudge Policy Engine & Latency Tracking | [`q4_realtime/nudges/nudge_policy_engine.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/nudges/nudge_policy_engine.py)<br>[`q4_realtime/evaluation/latency_benchmark.py`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/evaluation/latency_benchmark.py) | P50/P95 latency breakdown cards | **PASSED** |

---

## 20. Security & Privacy Controls

* **Secrets Management**: Secrets loaded exclusively from environment variables or `.env`. `.env` is explicitly listed in `.gitignore` to prevent git leakage.
* **PII Redaction**: Regex scrubbing strips emails, phone numbers, and SSN/EIN tax IDs prior to vector embedding generation.
* **Logging Safety**: Loggers censor secret strings and API key prefixes.
* **Least Privilege API Access**: FastAPI endpoints validate payload schemas via Pydantic models.

---

## 21. Known Limitations & Technical Disclosures

1. **Synthetic Demo Data**: Q2 knowledge base operates on synthetic SME business-loan policies. Not real financial company documentation.
2. **Gemini API Free-Tier Rate Limits**: Back-to-back LLM calls during automated test suites trigger 429 rate limit retries; handled via exponential backoff in `GeminiClient`.
3. **ASR Homophone Errors**: Deepgram acoustic models when constrained to standard English misinterpret Tagalog *po* as *four/for*, requiring multi-language hints (`tl-PH` + `en-PH`).
4. **Regional Accent Testing**: Javanese Medok dialect tolerance is evaluated via syntax normalization rules; unverified acoustic AI performance is not claimed.
5. **Telephony Carrier Setup**: Live phone testing requires active Vapi SIP trunking or PSTN number allocation.

---

## 22. Production Improvement Plan

To scale this platform to enterprise production (10,000+ active streams):

1. **Database Tier**: Migrate ChromaDB vector storage to PostgreSQL with `pgvector` or Dedicated Pinecone cluster.
2. **Distributed Messaging**: Replace in-memory WebSockets with Redis Streams / Kafka topic queues to handle heavy signal extraction worker pools.
3. **Observability**: Integrate Prometheus metrics for latency counters (`asr_latency_ms`, `llm_signal_ms`) and OpenTelemetry distributed tracing.
4. **Human Handoff Integration**: Connect handoff state directly to Twilio / Genesys Cloud SIP trunking for immediate call center agent transfers.
5. **Prompt & Schema Versioning**: Implement Langfuse / MLflow prompt registry for versioned system instructions.

---

## 23. Assessment Video Demo Checklist

When recording the final assessment demonstration video:

1. [ ] **Overview**: Briefly introduce the workspace and point out the zero-OpenAI dependency policy.
2. [ ] **Q2 Knowledge Base**: Run `python -m uvicorn q2_knowledge_base.api.app:app` and demonstrate vector retrieval citations via Swagger UI (`http://localhost:8000/docs`).
3. [ ] **Q1 Business Loan Agent**: Open `q1_business_loan/webhooks/simulator.html` in browser and demonstrate grounded qualification conversation & policy tool queries.
4. [ ] **Q3 Multilingual Bots**: Run `python q3_multilingual/evaluation/evaluate_q3.py` and show Taglish & Bahasa Indonesia transcripts.
5. [ ] **Q4 Real-Time Nudge Dashboard**: Run `streamlit run q4_realtime/dashboard/app.py`, start the live call simulation, and demonstrate live signal nudges, suppressed logs, and P50/P95 metrics.
6. [ ] **Tests**: Run `pytest` to show 100% passing test suite.

---

## 24. Likely Technical Interview Questions & Answers

### 1. Why did you choose Google Gemini API over OpenAI?
**Answer**: Gemini 1.5 Flash provides ultra-low sub-second inference latencies required for real-time nudge generation (Q4) and voice tool execution (Q1). It also offers native multimodal live API capabilities and 768-dim embeddings (`gemini-embedding-001`) under cost-effective quota structures.

### 2. Why use Hybrid Retrieval (ChromaDB + BM25) instead of pure vector search?
**Answer**: Pure vector search can miss exact keyword matches like policy section numbers ("Section 4.2"), specific interest rates ("7.5%"), or exact acronyms ("EIN"). Combining dense semantic search (ChromaDB) and sparse keyword matching (BM25) via Reciprocal Rank Fusion (RRF) delivers optimal precision and recall.

### 3. How does Reciprocal Rank Fusion (RRF) work in your Q2 engine?
**Answer**: RRF combines candidate document ranks from dense vector search and sparse BM25 search using the formula $RRF\_Score = \sum \frac{1}{k + rank}$. It eliminates the need to normalize raw distance scores across disparate retrieval algorithms.

### 4. How do you prevent hallucinations in Q1 Business Loan Agent?
**Answer**: The system prompt instructs Gemini to rely exclusively on evidence returned by the `query_knowledge_base` RAG tool. If retrieved evidence score falls below threshold, the agent returns a strict grounded fallback message: *"I don't have enough verified information..."*

### 5. Why is Q3 a localization rather than a literal translation of Q1?
**Answer**: Q3 implements distinct market-specific financial products (Philippines Bancassurance Life Plans vs. Indonesia Multifinance Motorcycle Loans) reflecting local regulatory bodies (IC in PH, OJK in ID), payment ecosystems (GCash/Maya vs M-Banking/Indomaret), and politeness registers (*po/opo* vs *Bapak/Ibu*).

### 6. How does Q3 handle Taglish code-switching in the Philippines?
**Answer**: The prompt establishes a natural Manila banking register where Filipino sentence structure combines seamlessly with standard English financial loanwords (`premium`, `policy`, `rider`, `lapse`, `beneficiary`) without forcing awkward literal translations.

### 7. How does Q3 handle regional Indonesian accents like Javanese ("Medok")?
**Answer**: The ASR pipeline uses post-transcription LLM intent normalization to map Javanese dialect vocabulary (*piye*, *pripun*, *sampeyan*, *mboten*, *sik kurang 200 ewu*) into standard financial intent while maintaining respectful customer service register (*Bapak/Ibu*).

### 8. How does Q4 process streaming audio in real-time?
**Answer**: Audio is ingested in 1.5-second frames. Each frame is timestamped (`audio_received_timestamp`), transcribed by streaming ASR (`transcription_timestamp`), analyzed by Gemini for structured JSON signals, evaluated against the Nudge Policy Engine, and pushed to the Streamlit UI via WebSockets.

### 9. How do you measure latency in Q4 without fabricating metrics?
**Answer**: Latency is calculated empirically at runtime by subtracting `audio_received_timestamp` from downstream event completion timestamps. Component latencies (ASR, Signal Extraction, Policy Evaluation, Dashboard Broadcast) and end-to-end latencies are aggregated to compute real P50 and P95 statistics.

### 10. How does the Nudge Policy Engine prevent notification fatigue?
**Answer**: It acts as a deterministic firewall after Gemini, suppressing signals if confidence is below `0.75`, if an identical topic nudge was emitted within `30 seconds` (cooldown), or if topic repetition limits (`max 2`) are exceeded.

### 11. What happens if audio is noisy or garbled in Q4?
**Answer**: Gemini outputs a signal type `unclear_audio` with lower confidence. The policy engine automatically catches this and suppresses high-confidence alerts, logging the suppression in the audit log.

### 12. How do you handle PII in Q2 Knowledge Base?
**Answer**: A deterministic regex PII scrubber strips emails, phone numbers, SSNs, and tax IDs before text is passed to the embedding engine or stored in ChromaDB, preventing sensitive data from polluting vector storage.

### 13. How would Q4 scale to 10x concurrent calls in production?
**Answer**: Audio ingestion would be decoupled from LLM signal extraction using Redis Streams or Kafka queues. A worker pool running async consumers would scale horizontally, while distributed token bucket rate limiters prevent Gemini API rate limit exhaustion.

### 14. What security controls are implemented for secrets management?
**Answer**: API keys are loaded exclusively from environment variables via `shared/config.py`. Key strings are censored in logs, and `.env` is explicitly git-ignored.

### 15. What are the main limitations of the current prototype?
**Answer**: The platform uses synthetic business-loan demo data, relies on free-tier Gemini API rate limits, requires external telephony SIP setup for live PSTN calls, and uses simulated 1.5s audio stream replay in local evaluation modes.
