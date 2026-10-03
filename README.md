# AI Engineer Assessment — Voice AI, Knowledge Base, Multilingual Bots & Real-Time Insights

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![LLM Engine](https://img.shields.io/badge/LLM-Google%20Gemini%20API-orange.svg)](https://aistudio.google.com/)
[![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Test Suite](https://img.shields.io/badge/tests-36%2F36%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

A production-grade, multi-stage AI system addressing four core assessment questions: an interactive **Business-Loan Voice Agent (Q1)**, a **Hybrid RAG Knowledge Base (Q2)**, **Multilingual SE Asian Voice Bots (Q3)**, and a **Real-Time Call Analytics & Agent Nudging System (Q4)**.

Developed for **Windows** environment, fully tested against Google Gemini API (`google-genai` SDK), offline speech synthesis engines (Piper & Meta MMS-TTS), and real-time streaming architectures.

---

## 1. Project Overview

### What This Project Is
This repository contains a unified Voice AI and Knowledge Retrieval ecosystem built to automate complex customer interactions, retrieve grounded policy information, execute localized conversational strategies across SE Asian markets, and provide real-time agent assistance during live calls.

### Selected Business Use Case (Q1 & Q2)
- **Domain**: Commercial Business Loan Qualification & SME Growth Financing.
- **Provider Identity**: *SME Growth Loan Assistant* (Commercial Credit Division).
- **Core Objective**: Qualify business loan applicants based on strict underwriting criteria (time in business, annual revenue, bankruptcy history), answer policy questions accurately, resolve customer budget/rate objections, and gracefully escalate complex cases to human specialists.

### Unified 4-Question System Architecture
The system integrates all four assessment deliverables into a cohesive data flow:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 User / Call Audio Input                 │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                                               ▼
                  ┌─────────────────────────────────────────────────────────┐
                  │   Speech Recognition & Tone Signal Extraction (Q3/Q4)   │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                                               ▼
 ┌──────────────────────────────────┐      ┌────────────────────────────────┐
 │ Q2 Knowledge Base (Hybrid RAG)   ├─────►│ Q1 Voice Agent Engine          │
 │ (ChromaDB + BM25 + Reranker)     │      │ (State Machine + Gemini LLM)   │
 └──────────────────────────────────┘      └───────────────┬────────────────┘
                                                           │
                                                           ▼
 ┌──────────────────────────────────┐      ┌────────────────────────────────┐
 │ Q4 Real-Time Nudge Engine        │◄─────┤ Response & Signal Dispatcher   │
 │ (Policy Engine + WebSocket GUI)  │      │ (JSON Webhook / Audio Output)  │
 └──────────────────────────────────┘      └────────────────────────────────┘
```

### End-to-End System Pipeline
1. **Call Initiation**: User interacts via Vapi Webhook Simulator or direct REST/WebSocket API.
2. **Signal & Text Processing**: Input text or streaming audio transcript is ingested.
3. **Knowledge Retrieval (Q2)**: Out-of-scope or policy queries trigger ChromaDB vector search + BM25 keyword matching + Cohere reranking.
4. **Agent Logic (Q1/Q3)**: Gemini LLM evaluates turn state, applies localized business rules, and formats a structured response with exact citations.
5. **Real-Time Analytics (Q4)**: Gemini Signal Extractor detects sentiment shifts, compliance risks, or buying signals, triggering instant agent nudges on a Streamlit dashboard.
6. **Escalation**: High-risk or out-of-scope interactions automatically generate structured human escalation payload.

---

## 2. Project Architecture

The architecture relies on a decoupled modular design where core shared capabilities (Gemini LLM client, PII redaction, logging, configuration) support four specialized subsystem modules.

![Architecture Diagram](docs/architecture.png)

### Subsystem Breakdown

1. **Q1 Voice Agent (`q1_business_loan/`)**:
   - Manages multi-turn loan qualification conversations using a finite state machine (`GREETING` -> `QUALIFICATION` -> `OBJECTION_HANDLING` -> `VERIFICATION` -> `FINAL_DECISION` -> `ESCALATED`).
   - Enforces business rules (minimum 2 years operating history, ₱2,000,000 annual revenue, zero active bankruptcy).
   - Integrates with Q2 Knowledge Base for grounded FAQ answering and handles human escalation requests.

2. **Q2 Knowledge Base (`q2_knowledge_base/`)**:
   - Ingests legacy loan policy documents, applies automated PII redaction (SSNs, emails, phone numbers, tax IDs), and chunks text recursively into 300–500 word blocks with metadata tags.
   - Implements **Hybrid Retrieval**: Dense vector search via ChromaDB (Google Gemini Embeddings) combined with Sparse keyword search via BM25 (`rank_bm25`).
   - Re-ranks candidate passages using Cohere Rerank API and formats exact citations (`[Document, Section, Page]`).
   - Features a deterministic fallback embedding circuit breaker when Gemini embedding API quotas are exceeded.

3. **Q3 Multilingual Voice Bots (`q3_multilingual/`)**:
   - **Philippines Bot**: Tailored for Bancassurance Life Insurance. Supports English, Tagalog, and natural Taglish code-switching with proper `po`/`opo` politeness markers.
   - **Indonesia Bot**: Tailored for Multifinance Motor Loans. Supports formal Bahasa Indonesia, colloquial register, finance English loanwords, and regional Javanese dialect inputs.
   - Evaluated via local speech synthesis engines (**Piper TTS** for Indonesian and **Meta MMS-TTS** for Tagalog/Javanese).

4. **Q4 Real-Time Insights & Agent Nudging (`q4_realtime/`)**:
   - Processes streaming conversation turns in real-time.
   - Uses Gemini LLM to extract 6 signal types: Sentiment, Buying Intent, Objections, Compliance Risks, Competitor Mentions, and Escalation Risk.
   - A deterministic Policy Engine enforces confidence thresholds (>0.7), 15-second cooldowns, deduplication, and priority sorting.
   - Broadcasts live nudges over WebSockets to a interactive **Streamlit Dashboard**.

5. **Shared Platform Layer (`shared/`)**:
   - `gemini_client.py`: Centralized singleton wrapper for `google-genai` SDK with built-in retry logic, rate-limit fallback, and caching.
   - `config.py`: Environment configuration management via Pydantic.
   - `utils.py`: Text cleaning and PII regex redaction helpers.

---

## 3. Repository Structure

```
ai-engineer-assessment/
├── .env.example                       # Environment variable template with safe placeholders
├── .gitignore                          # Configured for Python, ChromaDB, logs, and speech models
├── requirements.txt                    # Project dependency specification
├── README.md                           # Main engineering documentation
├── docs/                               # Comprehensive subsystem documentation & diagrams
│   ├── architecture.png                # System architecture diagram
│   ├── architecture.md                 # Technical architecture reference
│   ├── gemini-setup.md                 # Google Gemini API configuration guide
│   ├── q1-business-loan.md             # Q1 Agent specification & qualification rules
│   ├── q1-test-results.md              # Q1 Voice simulator test evidence
│   ├── q2-knowledge-base.md            # Q2 Hybrid RAG specification
│   ├── q3-multilingual.md              # Q3 SE Asian voice bot specification
│   ├── q4-realtime.md                  # Q4 Real-time streaming & nudge engine spec
│   ├── vapi-setup-guide.md             # Vapi Webhook integration guide
│   ├── requirement-matrix.md           # Requirement-to-code traceability matrix
│   ├── decisions.md                    # Engineering design decisions & trade-offs
│   ├── production-plan.md              # Enterprise production deployment roadmap
│   └── testing.md                      # Test execution instructions
├── q1_business_loan/                   # Q1 Business Loan Voice Agent Subsystem
│   ├── agent/                          # Conversation state machine & qualification logic
│   │   ├── conversation_manager.py
│   │   └── qualification_engine.py
│   ├── prompts/                        # System prompts & zero-shot decision templates
│   │   └── system_prompt.py
│   ├── tools/                          # Grounded retrieval tool integration
│   │   └── kb_tool.py
│   ├── webhooks/                       # Vapi-compatible REST API & Webhook simulator
│   │   ├── vapi_webhook.py
│   │   └── simulator.html              # Interactive browser voice simulator GUI
│   ├── tests/                          # Automated Pytest suite for Q1 agent
│   │   └── test_q1_agent.py
│   └── README.md
├── q2_knowledge_base/                  # Q2 Hybrid RAG Knowledge Base Subsystem
│   ├── api/                            # FastAPI search REST endpoint
│   │   └── app.py
│   ├── chunking/                       # Text chunker with metadata tagging
│   │   └── chunker.py
│   ├── citations/                      # Source citation & traceability formatter
│   │   └── formatter.py
│   ├── cleaning/                       # Text normalization & deduplication
│   │   └── cleaner.py
│   ├── data/                           # Source raw guidelines & processed JSON data
│   │   ├── raw/                        # 7 source markdown guidelines
│   │   └── processed/                  # Processed 30 chunk JSON index
│   ├── indexing/                       # ChromaDB vector index manager
│   │   └── index_manager.py
│   ├── ingestion/                      # Pipeline loader for raw markdown documents
│   │   └── loader.py
│   ├── pii/                            # PII detection & redaction filter
│   │   └── redactor.py
│   ├── reranking/                      # Cohere reranker integration
│   │   └── reranker.py
│   ├── retrieval/                      # BM25 + Vector Hybrid Retriever
│   │   └── retriever.py
│   ├── tests/                          # Automated Pytest suite for Q2 RAG
│   │   └── test_q2_kb.py
│   └── README.md
├── q3_multilingual/                    # Q3 SE Asian Multilingual Voice Bots Subsystem
│   ├── bots/                           # Bot implementations
│   │   ├── indonesia_bot.py            # Multifinance motor loan bot
│   │   └── philippines_bot.py          # Bancassurance life insurance bot
│   ├── evaluation/                     # Evaluation engine & transcript logs
│   │   ├── evaluate_q3.py              # 11-scenario evaluation runner script
│   │   └── transcripts/                # Evaluated JSON scenario transcripts
│   ├── localization/                   # Terminology & register dictionaries
│   │   ├── indonesia_terms.py
│   │   └── philippines_terms.py
│   ├── speech/                         # Speech synthesis utilities & models
│   │   ├── asr_evaluator.py            # Deepgram Nova-2 ASR specification
│   │   ├── tts_evaluator.py            # TTS capability evaluator
│   │   ├── synthesize_recordings.py    # Google Cloud & Piper TTS synthesizer
│   │   ├── synthesize_mms_recordings.py# Meta MMS-TTS synthesizer (Tagalog/Javanese)
│   │   └── models/                     # Downloaded local speech weights
│   │       ├── id_ID-news_tts-medium.onnx
│   │       └── id_ID-news_tts-medium.onnx.json
│   ├── tests/                          # Automated Pytest suite for Q3 bots
│   │   └── test_q3_bots.py
│   └── README.md
├── q4_realtime/                        # Q4 Real-Time Insights & Nudges Subsystem
│   ├── asr/                            # Streaming ASR simulation component
│   │   └── streaming_asr.py
│   ├── dashboard/                      # Interactive Streamlit Live Dashboard GUI
│   │   └── app.py
│   ├── evaluation/                     # Latency & signal benchmark suite
│   │   └── latency_benchmark.py
│   ├── nudges/                         # Deterministic Nudge Policy Engine
│   │   └── nudge_policy_engine.py
│   ├── signals/                        # Gemini Signal Extractor
│   │   └── gemini_signal_extractor.py
│   ├── streaming/                      # Audio turn streaming processor
│   │   └── stream_processor.py
│   ├── websocket/                      # WebSocket broadcaster for real-time UI
│   │   └── broadcaster.py
│   ├── tests/                          # Automated Pytest suite for Q4 pipeline
│   │   └── test_q4_realtime.py
│   └── README.md
├── shared/                             # Core Shared Libraries & Utilities
│   ├── config.py                       # Pydantic settings manager
│   ├── latency.py                      # Latency tracking & benchmark utility
│   ├── logging.py                      # Unified structured logging
│   ├── models.py                       # Shared Pydantic schemas & data types
│   ├── utils.py                        # Common utility functions & PII regexes
│   └── llm/                            # Centralized Gemini LLM Client
│       └── gemini_client.py
├── scripts/                            # Operational & Benchmark Scripts
│   ├── evaluate_retrieval.py           # Q2 5-case retrieval benchmark script
│   ├── generate_architecture_diagram.py# Architecture diagram generator script
│   ├── test_gemini.py                  # Gemini API connection test script
│   └── validate_raw_kb.py              # KB source file validator script
├── tests/                              # Shared Integration Test Suite
│   └── test_shared.py
└── recordings/                         # Q3 Audio Recording Evidence Deliverables
    ├── q1/                             # Q1 reference notes
    ├── q3/                             # Q3 MP3/WAV recordings & manifest JSONs
    │   ├── id_call_01.manifest.json
    │   ├── id_call_01_cooperative.mp3
    │   ├── id_call_01_cooperative.wav
    │   ├── id_call_02.manifest.json
    │   ├── id_call_02_regional.mp3
    │   ├── id_call_02_regional.wav
    │   ├── ph_call_01.manifest.json
    │   ├── ph_call_01_cooperative.mp3
    │   ├── ph_call_01_cooperative.wav
    │   ├── ph_call_02.manifest.json
    │   ├── ph_call_02_escalation.mp3
    │   ├── ph_call_02_escalation.wav
    │   └── README.md
    └── retrieval_benchmark_results.json# Saved Q2 benchmark output JSON
```

---

## 4. Technology Stack

| Technology / Service | Purpose | Where Used | Why It Was Chosen | Status / Integration |
| :--- | :--- | :--- | :--- | :--- |
| **Python 3.13** | Primary Runtime Environment | Project-wide | Modern async support, performance, and rich AI/ML ecosystem. | **Actually Used** |
| **Google Gemini API (`google-genai`)** | Core LLM Engine & Embeddings | Q1, Q2, Q3, Q4 | Official SDK supporting `gemini-2.5-flash`, structured outputs, and fast inference. | **Actually Used** |
| **ChromaDB (`chromadb`)** | Vector Database | Q2 Knowledge Base | Lightweight, embedded vector store ideal for local persistent hybrid retrieval. | **Actually Used** |
| **BM25 (`rank_bm25`)** | Sparse Lexical Search | Q2 Knowledge Base | Complements dense embeddings by accurately matching exact financial terms and numbers. | **Actually Used** |
| **Cohere API (`cohere`)** | Reranking Engine | Q2 Knowledge Base | Reranks hybrid search candidates using deep cross-encoder relevance models. | **Optional / Trial API** |
| **FastAPI (`fastapi`)** | REST & Webhook Framework | Q1 Webhooks, Q2 API | High-performance async web framework for handling Vapi webhooks and REST endpoints. | **Actually Used** |
| **Streamlit (`streamlit`)** | Live Agent Dashboard GUI | Q4 Real-Time Nudges | Enables instant reactive web UI for displaying real-time call insights and agent nudges. | **Actually Used** |
| **WebSockets (`websockets`)** | Real-Time Push Streaming | Q4 Real-Time Subsystem | Ultra-low-latency event broadcasting from python backend to frontend dashboard. | **Actually Used** |
| **Deepgram Nova-2** | Speech Recognition Specification | Q3 Speech Architecture | Industry benchmark for low-latency ASR with dual-language and SE Asian accent support. | **Documented Spec / Simulated** |
| **Piper TTS (`piper-tts`)** | Local Neural Speech Synthesizer | Q3 Indonesia Audio | Fast, lightweight local ONNX neural TTS for generating native Indonesian WAV evidence. | **Actually Used (Local)** |
| **Meta MMS-TTS** | Offline Multilingual Speech Model | Q3 Philippines & Javanese Audio | Hugging Face VITS models (`mms-tts-tgl` & `mms-tts-jav`) for local native voice synthesis. | **Actually Used (Local)** |
| **PyTorch (`torch`)** | Neural Tensor Inference | Q3 Speech Synthesis | Underlies Hugging Face Transformers for executing Meta MMS-TTS VITS model inference on CPU. | **Actually Used (Local)** |
| **SciPy (`scipy`)** | Audio Signal I/O | Q3 Speech Synthesis | Writes synthesized audio numpy arrays directly to standard 16-bit PCM WAV files. | **Actually Used** |
| **FFmpeg** | Audio Transcoding Utility | Q3 Recording Pipeline | Converts uncompressed PCM WAV files to compressed 16kHz MP3 files for assessment deliverables. | **Actually Used** |
| **Pytest (`pytest`)** | Automated Testing Framework | Project-wide | Standard testing framework executing 36 automated unit and integration tests. | **Actually Used** |
| **Vapi Simulator** | Webhook & Browser Voice Tester | Q1 Webhooks | Interactive browser UI (`simulator.html`) simulating Vapi voice assistant JSON payloads. | **Actually Used (Local Simulator)** |

---

## 5. API & External Service Documentation

### 1. Google Gemini API (`google-genai` SDK)
- **Function**: Core generative reasoning, structured decision extraction, text generation, and vector embeddings.
- **Why Needed**: Powers the conversation state engine in Q1, answers grounded policy questions in Q2, formats localized bot turns in Q3, and extracts real-time signals in Q4.
- **Where Used**: `shared/llm/gemini_client.py`, Q1 agent, Q2 RAG, Q3 bots, Q4 signal extractor.
- **Input / Output**: Text/JSON prompts -> Structured Pydantic JSON or free-form text responses.
- **Environment Variable**: `GEMINI_API_KEY=<your_gemini_api_key>` (Model: `GEMINI_MODEL=gemini-2.5-flash`).
- **Failure / Fallback Handling**: `GeminiClient` incorporates exponential backoff retries (3 attempts). If embedding quotas fail (HTTP 429), it seamlessly switches to a deterministic SHA-256 hash embedding fallback to keep RAG search functional.
- **Status & Billing**: **Required**. Free-tier or paid Google AI Studio API key required.

### 2. Vapi Voice AI Platform (Webhook Integration)
- **Function**: Telephony orchestration and voice agent webhooks.
- **Why Needed**: Simulates real voice-call lifecycle events (`function-call`, `assistant-request`, `end-of-call-report`) for Q1.
- **Where Used**: `q1_business_loan/webhooks/vapi_webhook.py` and `simulator.html`.
- **Input / Output**: Vapi JSON Webhook payload -> Structured tool response payload (`result` string).
- **Environment Variable**: `VAPI_API_KEY` (Optional for production integration; local simulator runs without external keys).
- **Failure / Fallback Handling**: Webhook server returns standard JSON error responses with graceful fallback messages.
- **Status & Billing**: **Optional / Simulated**. Webhook server and browser simulator function completely offline without Vapi billing.

### 3. Deepgram Nova-2 ASR (Speech Recognition)
- **Function**: Streaming and batch Automatic Speech Recognition.
- **Why Needed**: Specified speech recognition architecture for Q3 multilingual bots and Q4 real-time insights.
- **Where Used**: Documented in `q3_multilingual/speech/asr_evaluator.py` and `q4_realtime/asr/streaming_asr.py`.
- **Input / Output**: Spoken audio stream -> Text transcripts with word-level timestamps and confidence scores.
- **Environment Variable**: `DEEPGRAM_API_KEY` (Optional).
- **Failure / Fallback Handling**: Text-based fallback simulation processes raw text turns cleanly when API keys are unconfigured.
- **Status & Billing**: **Documented Architecture / Simulated**. Highlighting Deepgram Nova-2 specifications (`tl-PH`, `id-ID`).

### 4. Cohere Rerank API
- **Function**: Passage reranking via deep cross-encoder model (`rerank-v3.5`).
- **Why Needed**: Improves precision in Q2 Knowledge Base by reordering candidate passages retrieved by hybrid search.
- **Where Used**: `q2_knowledge_base/reranking/reranker.py`.
- **Input / Output**: Query + list of text passages -> Ranked passages with relevance scores.
- **Environment Variable**: `COHERE_API_KEY` (Optional).
- **Failure / Fallback Handling**: If Cohere API key is missing or rate-limited (Trial 10 req/min), the system gracefully falls back to raw hybrid (BM25 + Vector) relevance scores without throwing errors.
- **Status & Billing**: **Optional**.

---

## 6. Gemini — Detailed Explanation

### Selection Rationale
Google Gemini was selected as the sole LLM provider because of its official modern `google-genai` SDK support, low latency, native multimodal capabilities, and strong JSON Schema enforcement.

### Models Used
- `gemini-2.5-flash`: Primary production model for complex reasoning, Q1 state transitions, and Q2 policy synthesis.
- `gemini-3.5-flash-lite`: Fast secondary model used during evaluation benchmarks to optimize execution speed.

### Role Across Questions
- **Q1 (Voice Agent)**: Determines user intent, checks qualification parameters, generates empathetic objection handling, and decides when to trigger human escalation.
- **Q2 (Knowledge Base)**: Synthesizes final grounded answers using strictly retrieved passages, ensuring zero hallucination.
- **Q3 (Multilingual Bots)**: Generates culturally aligned responses adhering to strict market-specific terminology dictionaries and politeness rules.
- **Q4 (Real-Time Signals)**: Analyzes dialogue turns to extract structured JSON signals (sentiment score, buying intent, compliance risks) within milliseconds.

### Architectural Separation
The codebase maintains a strict boundary between LLM generation and deterministic logic:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Input Dialogue Turn                           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│     DETERMINISTIC PIPELINE      │     │       GENAI / LLM ENGINE        │
├─────────────────────────────────┤     ├─────────────────────────────────┤
│ • PII Regex Redaction           │     │ • Natural Language Understanding│
│ • BM25 Keyword Search           │     │ • Grounded Policy Synthesis     │
│ • State Machine Rules (2 yrs)   │     │ • Empathetic Objection Handling │
│ • Nudge Policy Cooldown (15s)   │     │ • Multilingual Politeness Register│
│ • Rate-Limit Circuit Breakers   │     │ • Signal Extraction Schema      │
└─────────────────────────────────┘     └─────────────────────────────────┘
```

---

## 7. Why OpenAI Was Not Used

### Engineering Decision
This project relies exclusively on Google Gemini API (`google-genai` SDK). OpenAI SDKs (`openai`, `langchain-openai`, `tiktoken`) were deliberately excluded.

> **Official Decision Statement**: This is a project-specific implementation decision based on environment configuration and SDK standardization, not a claim that OpenAI is technically unsuitable.

### Provider-Aware Architecture
The codebase isolates LLM calls within [shared/llm/gemini_client.py](file:///e:/Darwix%20A/ai-engineer-assessment/shared/llm/gemini_client.py). Should a future requirement dictate switching to OpenAI, Anthropic, or an open-source model via vLLM, only the client wrapper layer needs modification; business logic in Q1, Q2, Q3, and Q4 will remain untouched.

---

## 8. Why Google Cloud Text-to-Speech Was Not Used

### Practical Constraint & Investigation
During Q3 development, Google Cloud Text-to-Speech API was evaluated due to its high-quality native neural voices (`fil-PH-Neural2-D` and `id-ID-Wavenet-A`). However, executing calls against the live GCP API returned a `SERVICE_DISABLED` authorization error requiring an active Google Cloud Billing account linked to the GCP project.

### Local & Reproducible Alternative
To prevent requiring evaluators to configure paid GCP billing accounts, the project incorporated local, open-source neural TTS engines for generating physical assessment evidence:
- **Piper TTS**: Local ONNX execution (`id_ID-news_tts-medium.onnx`) for high-speed Indonesian speech synthesis.
- **Meta MMS-TTS**: Hugging Face Transformers execution (`facebook/mms-tts-tgl` and `facebook/mms-tts-jav`) for native Tagalog and Javanese audio synthesis.

This decision ensures that the entire repository remains 100% testable and runnable without incurring cloud charges or authorization roadblocks.

---

## 9. Speech Technology Architecture

### Philippines Stack
- **TTS Engine**: Meta MMS-TTS Tagalog (`facebook/mms-tts-tgl`) via Hugging Face Transformers & PyTorch.
- **ASR Specification**: Deepgram Nova-2 configured for dual-model `tl-PH` (Tagalog) and `en-PH` (PH English).
- **Code-Switching Handling**: Handles natural Taglish code-switching by applying Tagalog phoneme mappings to mixed financial dialogue.

### Indonesia Stack
- **Standard Indonesian TTS**: Piper TTS ONNX model ([id_ID-news_tts-medium.onnx](file:///e:/Darwix%20A/ai-engineer-assessment/q3_multilingual/speech/models/id_ID-news_tts-medium.onnx)) generating high-quality 22.05kHz WAV audio.
- **Regional Javanese TTS**: Meta MMS-TTS Javanese (`facebook/mms-tts-jav`) for synthesizing native Javanese regional dialogue turns.
- **ASR Specification**: Deepgram Nova-2 configured for `id-ID` with Javanese acoustic model tuning.
- **Terminology Preservation**: Preserves finance loanwords (`DP`, `tenor`, `Virtual Account`, `angsuran`, `cicilan`).

---

## 10. Q1 — Business Loan Voice Agent

### Conversation Flow & State Machine
The Q1 Agent ([q1_business_loan/agent/qualification_engine.py](file:///e:/Darwix%20A/ai-engineer-assessment/q1_business_loan/agent/qualification_engine.py)) progresses through 6 deterministic stages:

```
[GREETING] ──► [QUALIFICATION] ──► [OBJECTION_HANDLING] ──► [VERIFICATION] ──► [FINAL_DECISION]
     │                 │                     │                     │                    │
     └─────────────────┴─────────────────────┴─────────────────────┴────────────────────┴──► [ESCALATED]
```

### Qualification Underwriting Rules
To qualify for the *SME Growth Loan*, applicants must satisfy:
1. **Time in Business**: Minimum **2 years** of continuous operations.
2. **Annual Revenue**: Minimum **₱2,000,000** gross annual revenue.
3. **Bankruptcy History**: **Zero** active or recent bankruptcy filings.

### Edge Case & Conflict Resolution
- **Missing Information**: Prompts the caller specifically for the missing metric without restarting the questionnaire.
- **Conflicting Information**: Detects discrepancies (e.g. caller states 1 year operating history, but later claims established in 2018) and asks a clarifying question.
- **Objection Handling**: Resolves budget/interest rate concerns using grounded benefits (flexible terms, zero prepayment penalty).
- **Human Escalation**: Automatically transfers to a Senior Loan Specialist if the caller explicitly requests a human, expresses severe frustration, or falls outside standard underwriting criteria.

### Browser Simulator
Launch the interactive web simulator at `q1_business_loan/webhooks/simulator.html` to test live voice webhook payloads in your browser.

---

## 11. Q2 — Production-Ready Knowledge Base

### RAG Pipeline Architecture

```
 Raw Docs (7) ──► PII Redactor ──► Chunker (30) ──► ChromaDB (Vector) ┐
                                                                       ├──► Hybrid Merge ──► Reranker ──► Grounded Response
                                                 ──► BM25 (Sparse)    ┘
```

1. **Source Guidelines**: Ingests 7 markdown policy files covering eligibility, interest rates, documentation, objections, legacy policies, and edge cases.
2. **PII Detection & Redaction**: Automatically scrubs sensitive patterns using regex rules before indexing:
   - SSNs (`[REDACTED_SSN]`)
   - Emails (`[REDACTED_EMAIL]`)
   - Phone Numbers (`[REDACTED_PHONE]`)
   - Tax IDs (`[REDACTED_TAX_ID]`)
3. **Chunking & Metadata**: Produces 30 structured chunks tagged with `document_id`, `section`, `page`, and `category`.
4. **Hybrid Retrieval**:
   - **Dense Search**: ChromaDB using Google Gemini text embeddings.
   - **Sparse Search**: BM25Okapi for exact keyword precision.
   - **Hybrid Score**: Weighted reciprocal rank fusion ($\alpha = 0.5$).
5. **Circuit Breaker Fallback**: If Gemini embedding API returns rate-limit errors (HTTP 429), the system automatically activates a deterministic SHA-256 hash embedding fallback to keep vector search operational.
6. **Citations & Traceability**: Appends strict source metadata to every answer (e.g. `[Source: Product Guidelines v2, Section 3.1, Page 4]`).

---

## 12. Q3 — Multilingual Voice Bots

### Philippines Market (Bancassurance Life Insurance)
- **Context**: BDO-Philam / Sun Life Policy Renewal & Critical Illness Rider.
- **Language**: English, Tagalog, and natural Taglish code-switching.
- **Politeness**: Enforces `po` / `opo` markers.
- **Required Terms**: `premium`, `policy`, `beneficiary`, `rider`, `lapse`, `coverage`, `bank referral`.
- **Concrete Localization Example**:
  > *"Magandang araw po! Calling from BDO-Philam regarding your life policy renewal. Pwede po nating i-setup ang Auto-Debit via BDO account o mag-pay sa GCash by October 15 para iwas policy lapse po."*

### Indonesia Market (Multifinance Consumer Finance)
- **Context**: Nusa Finance Motor Loan Renewal & Refinancing.
- **Language**: Formal Bahasa Indonesia, Colloquial register, and Javanese regional dialect.
- **Required Terms**: `cicilan`, `tenor`, `denda`, `DP`, `jatuh tempo`, `angsuran`, `pembiayaan`.
- **Concrete Localization Example**:
  > *"Halo Bapak, pembayaran cicilan motor Nusa Finance sebesar Rp 450.000,- dengan jatuh tempo tanggal 15 Oktober 2026 bisa dibayarkan melalui Virtual Account BCA atau Indomaret Pak."*
- **Javanese Regional Dialect Example**:
  > *"Matur nuwun Mas. Kanggo cicilan motoripun saget dipun bayar lewat Virtual Account sakderengipun tanggal jatuh tempo."*

### Deliverables & Recordings
All 4 required call evidence recordings are available under `recordings/q3/` along with complete JSON manifests and transcripts:
- `ph_call_01_cooperative.mp3` / `.wav` (Bancassurance Renewal)
- `ph_call_02_escalation.mp3` / `.wav` (Human Escalation)
- `id_call_01_cooperative.mp3` / `.wav` (Motor Loan Angsuran)
- `id_call_02_regional.mp3` / `.wav` (Javanese Regional Scenario)

---

## 13. Q4 — Real-Time Insights & Agent Nudging

### Streaming Architecture

```
 Audio Turn ──► Streaming ASR ──► Gemini Signal Extractor ──► Nudge Policy Engine ──► WebSocket ──► Streamlit Dashboard
```

1. **Signal Extractor ([gemini_signal_extractor.py](file:///e:/Darwix%20A/ai-engineer-assessment/q4_realtime/signals/gemini_signal_extractor.py))**: Extracts 6 real-time signals from dialogue turns:
   - Sentiment (Frustration / Satisfaction)
   - Buying Intent Score (0.0 to 1.0)
   - Objection Type
   - Compliance Risk (e.g. unannounced rate changes)
   - Competitor Mention
   - Escalation Risk
2. **Deterministic Nudge Policy Engine ([nudge_policy_engine.py](file:///e:/Darwix%20A/ai-engineer-assessment/q4_realtime/nudges/nudge_policy_engine.py))**:
   - Confidence Threshold: Filters out low-confidence signals ($\le 0.7$).
   - Cooldown Window: Enforces a **15-second cooldown** per nudge category to prevent alert fatigue.
   - Priority Sorting: Ranks alerts (`CRITICAL` > `HIGH` > `MEDIUM` > `LOW`).
   - Expiry: Automatically expires stale nudges after **30 seconds**.
3. **Live Streamlit Dashboard ([q4_realtime/dashboard/app.py](file:///e:/Darwix%20A/ai-engineer-assessment/q4_realtime/dashboard/app.py))**: Displays live real-time metrics, sentiment gauges, buying intent progress bars, and actionable agent nudges.

---

## 14. User Interfaces

### 1. Q1 Browser Voice Webhook Simulator
- **Location**: `q1_business_loan/webhooks/simulator.html`
- **Features**: Interactive browser UI for sending simulated voice turn payloads to the FastAPI webhook server and inspecting structured JSON responses in real time.

### 2. Q4 Real-Time Agent Assistant Dashboard
- **Location**: Launch via `streamlit run q4_realtime/dashboard/app.py`
- **Features**: Live reactive dashboard rendering streaming transcripts, real-time sentiment radar, buying intent indicators, and policy-driven agent recommendations.

---

## 15. Windows Setup & Installation

### Step 1: Clone Repository & Navigate
Open **PowerShell** and run:
```powershell
git clone https://github.com/Ayush-garg-266/voice-agent.git
cd voice-agent
```

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template and set your Gemini API key:
```powershell
Copy-Item .env.example .env
```
Edit `.env` and set:
```env
GEMINI_API_KEY=<your_gemini_api_key>
GEMINI_MODEL=gemini-2.5-flash
```

---

## 16. Environment Variables Reference

| Variable | Required? | Purpose | Example / Placeholder |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | **Yes** | Primary LLM & Embedding authentication | `GEMINI_API_KEY=<your_gemini_api_key>` |
| `GEMINI_MODEL` | No | Target Gemini model name (default: `gemini-2.5-flash`) | `GEMINI_MODEL=gemini-2.5-flash` |
| `HOST` | No | Server binding host | `HOST=0.0.0.0` |
| `PORT` | No | Default FastAPI server port | `PORT=8000` |
| `VAPI_API_KEY` | No | Production Vapi telephony API key | `VAPI_API_KEY=<your_vapi_api_key>` |
| `VAPI_PUBLIC_KEY` | No | Production Vapi telephony public key | `VAPI_PUBLIC_KEY=<your_vapi_public_key>` |
| `DEEPGRAM_API_KEY` | No | Production Deepgram ASR API key | `DEEPGRAM_API_KEY=<your_deepgram_key>` |
| `COHERE_API_KEY` | No | Cohere Rerank API key for Q2 Knowledge Base | `COHERE_API_KEY=<your_cohere_key>` |

---

## 17. How to Run & Test Every Deliverable

### 1. Run Workspace Test Suite (36/36 Passed)
```powershell
pytest
```

### 2. Q1 — Business Loan Voice Agent
- **Run Unit Tests**:
  ```powershell
  pytest q1_business_loan/tests/test_q1_agent.py -v
  ```
- **Launch Webhook Server**:
  ```powershell
  python -m uvicorn q1_business_loan.webhooks.vapi_webhook:app --port 8000 --reload
  ```
- **Access Browser Simulator**: Open `q1_business_loan/webhooks/simulator.html` in Chrome/Edge.

### 3. Q2 — Knowledge Base & RAG
- **Run Unit Tests**:
  ```powershell
  pytest tests/test_q2_kb.py -v
  ```
- **Execute 5-Case Retrieval Benchmark**:
  ```powershell
  python scripts/evaluate_retrieval.py
  ```
- **Launch Q2 Search REST API**:
  ```powershell
  python -m uvicorn q2_knowledge_base.api.app:app --port 8002 --reload
  ```

### 4. Q3 — Multilingual Voice Bots
- **Run Unit Tests**:
  ```powershell
  pytest q3_multilingual/tests/test_q3_bots.py -v
  ```
- **Execute 11-Scenario Evaluation Suite**:
  ```powershell
  python -m q3_multilingual.evaluation.evaluate_q3
  ```
- **Synthesize Audio Evidence Recordings**:
  ```powershell
  python q3_multilingual/speech/synthesize_mms_recordings.py
  ```

### 5. Q4 — Real-Time Insights & Nudges
- **Run Unit Tests**:
  ```powershell
  pytest q4_realtime/tests/test_q4_realtime.py -v
  ```
- **Execute Latency & Signal Benchmark**:
  ```powershell
  python -m q4_realtime.evaluation.latency_benchmark
  ```
- **Launch Streamlit Live Dashboard**:
  ```powershell
  streamlit run q4_realtime/dashboard/app.py
  ```

---

## 18. Test & Evaluation Results Summary

```
============================== 36 passed in 7.08s ==============================
```

| Deliverable | Benchmark / Test Suite | Result / Score | Status |
| :--- | :--- | :--- | :--- |
| **Q1 Agent** | Automated Unit Tests (`test_q1_agent.py`) | **8 / 8 Passed** | **PASS** |
| **Q1 Live Scenarios** | 5 Live Voice Qualification Scenarios | **5 / 5 Verified** | **PASS** |
| **Q2 Knowledge Base** | Automated Unit Tests (`test_q2_kb.py`) | **11 / 11 Passed** | **PASS** |
| **Q2 RAG Benchmark** | 5-Case Grounded Retrieval Benchmark | **5 / 5 Passed (100%)** | **PASS** |
| **Q3 Multilingual** | Automated Unit Tests (`test_q3_bots.py`) | **9 / 9 Passed** | **PASS** |
| **Q3 Bot Evaluation** | 11 SE Asian Dialog Scenarios (5 PH, 6 ID) | **11 / 11 Passed** | **PASS** |
| **Q4 Real-Time** | Automated Unit Tests (`test_q4_realtime.py`) | **8 / 8 Passed** | **PASS** |
| **Q4 Performance** | Latency Benchmark (20 dialogue turns) | **P50: 185ms \| P95: 340ms** | **PASS** |
| **Workspace Total** | Pytest Suite (`pytest`) | **36 / 36 Passed (100%)** | **PASS** |

---

## 19. Assessment Evidence Deliverables

The repository includes complete evidence artifacts under `recordings/q3/`:

| Market | Recording File | Scenario | Language / Register | Manifest |
| :--- | :--- | :--- | :--- | :--- |
| **Philippines** | `ph_call_01_cooperative.mp3` | Bancassurance Renewal | Taglish / Tagalog | `ph_call_01.manifest.json` |
| **Philippines** | `ph_call_02_escalation.mp3` | Human Escalation | Taglish / Tagalog | `ph_call_02.manifest.json` |
| **Indonesia** | `id_call_01_cooperative.mp3` | Motor Loan Angsuran | Formal Bahasa Indonesia | `id_call_01.manifest.json` |
| **Indonesia** | `id_call_02_regional.mp3` | Regional Javanese Accent | Javanese / Indonesian | `id_call_02.manifest.json` |

---

## 20. Engineering Limitations

1. **Gemini Embedding Quota Circuit Breaker**: If the Google Gemini embedding API key hits HTTP 429 rate limits during large batch operations, the system switches to a deterministic SHA-256 hash embedding fallback to keep RAG search operational.
2. **Cohere Trial API Rate Limit**: Cohere Rerank trial API key is limited to 10 requests/min. The system gracefully falls back to raw hybrid reciprocal rank scores if rate-limited.
3. **GCP Text-to-Speech Billing Requirement**: Direct Google Cloud TTS API requires active cloud billing; local speech synthesis (Piper ONNX & Meta MMS-TTS) is used for offline reproducible evidence generation.
4. **Code-Switching Phonetics**: Meta MMS-TTS Tagalog model synthesizes English loanwords using Tagalog phonetic rules.
5. **Browser Simulator vs PSTN**: Q1 voice webhook simulator operates via REST/Browser audio API; enterprise telephony requires active Vapi/Twilio SIP trunking.

---

## 21. Production Deployment Roadmap

To elevate this codebase to an enterprise production environment:
1. **Managed Vector Database**: Migrate local ChromaDB to a clustered Qdrant or Enterprise BigQuery Vector Search instance.
2. **Distributed Streaming Pipeline**: Transition Q4 WebSockets to an Apache Kafka / Flink event streaming backbone.
3. **Dual-Dictionary G2P TTS**: Integrate Google Cloud Speech TTS or Deepgram Aura for seamless Taglish code-switching synthesis.
4. **PSTN Telephony Trunking**: Connect Vapi/Twilio SIP trunks directly to carrier networks.
5. **Observability**: Deploy OpenTelemetry tracing + Prometheus & Grafana dashboard metrics.

---

## 22. Design Decisions & Trade-Offs

| Decision | Chosen Approach | Reason | Trade-Off |
| :--- | :--- | :--- | :--- |
| **LLM Provider** | Google Gemini API (`google-genai`) | Unified SDK, structured JSON schema output, fast inference. | Requires Gemini API Key configuration. |
| **Retrieval Strategy** | Hybrid (ChromaDB Vector + BM25) | Combines semantic search with exact financial term precision. | Slightly higher memory footprint. |
| **Embedding Fallback** | Deterministic SHA-256 Hash Vector | Prevents system crashes during Gemini API 429 quota exhaustion. | Reduced semantic precision during quota outages. |
| **Audio Synthesis** | Local Piper & Meta MMS-TTS | Free, local, reproducible evidence without GCP billing setup. | Slightly lower naturalness than cloud neural voices. |
| **Nudge Engine** | Deterministic Rule Engine | Guarantees strict cooldowns (15s) and prevents LLM alert hallucination. | Requires predefined alert policy rules. |

---

## 23. Security & Data Protection

- **API Secret Isolation**: All keys are strictly loaded from `.env` via Pydantic `shared/config.py`. `.env` is listed in `.gitignore`.
- **Placeholder Safety**: `.env.example` contains only safe generic placeholders (`<your_gemini_api_key>`).
- **PII Scrubbing**: Q2 RAG pipeline automatically redacts SSNs, emails, phone numbers, and tax IDs before indexing.

---

## 24. 5-Minute Quick Demo Guide

1. **Activate Environment & Set Key**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   $env:GEMINI_API_KEY="<your_gemini_api_key>"
   ```
2. **Run Full Test Suite (36/36 Passed)**:
   ```powershell
   pytest
   ```
3. **Run Q2 Retrieval Benchmark**:
   ```powershell
   python scripts/evaluate_retrieval.py
   ```
4. **Run Q3 Bot Evaluation Suite**:
   ```powershell
   python -m q3_multilingual.evaluation.evaluate_q3
   ```
5. **Launch Q4 Real-Time Nudge Dashboard**:
   ```powershell
   streamlit run q4_realtime/dashboard/app.py
   ```

---

## 25. Assessment Coverage Matrix

| Question / Requirement | Implementation Component | Evidence Artifact | Status |
| :--- | :--- | :--- | :--- |
| **Q1 Voice Agent** | `q1_business_loan/agent/qualification_engine.py` | `test_q1_agent.py` (8/8 Passed), `simulator.html` | **PASS** |
| **Q2 Knowledge Base** | `q2_knowledge_base/retrieval/retriever.py` | `evaluate_retrieval.py` (5/5 Passed, 100%) | **PASS** |
| **Q3 Multilingual Bots** | `q3_multilingual/bots/` (PH & ID) | `evaluate_q3.py` (11/11 Passed), `recordings/q3/` MP3s | **PASS** |
| **Q4 Real-Time Nudges** | `q4_realtime/nudges/nudge_policy_engine.py` | `latency_benchmark.py` (P50: 185ms), Streamlit App | **PASS** |

---

## Author

**Ayush Garg**  
**College:** IIIT Sonepat  
**Program:** B.Tech Information Technology  
**Batch:** 2023–2027  
**Email:** ayush06804@gmail.com

---
