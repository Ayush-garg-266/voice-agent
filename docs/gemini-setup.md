# Google Gemini API Setup & Architectural Guide

## 1. Overview & Policy Statement

This project relies **exclusively on the Google Gemini API** (`google-genai` SDK) for all machine learning, reasoning, knowledge grounding (RAG), and real-time audio signal extractions.

> ⚠️ **Strict OpenAI-Free Policy**: There are **zero** OpenAI SDKs, APIs, packages, or models used in this codebase. Packages such as `openai`, `langchain-openai`, `tiktoken`, or `ChatOpenAI` are strictly forbidden and omitted.

---

## 2. How to Obtain a Google Gemini API Key

1. Navigate to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on **Get API key** in the left navigation sidebar.
4. Click **Create API key** (either in a new GCP project or an existing project).
5. Copy the generated API key string (e.g. `<your_gemini_api_key>`).

---

## 3. How to Configure `.env`

1. In the project root directory (`ai-engineer-assessment/`), copy the `.env.example` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and paste your key:
   ```env
   GEMINI_API_KEY=<your_gemini_api_key>
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. Save the file. Ensure `.env` is listed in `.gitignore` so secrets are never committed to version control.

---

## 4. How to Test Gemini API Setup

Run the verification test script:

```bash
python scripts/test_gemini.py
```

### Expected Output (Success):
```text
============================================================
  Phase 1: Google Gemini API Connectivity Test
============================================================
[*] API Key Status: Configured (AIza...Key)
[*] Target Model:   gemini-2.5-flash
[*] Initiating minimal Gemini API test call...

------------------------------------------------------------
  Gemini API Response:
------------------------------------------------------------
Hello! Connection to Google Gemini API is active and functioning properly.
------------------------------------------------------------

[SUCCESS] Phase 1 Gemini connection verified successfully!
```

---

## 5. How Gemini is Used Across the Platform

The central client located at `shared/llm/gemini_client.py` (`GeminiClient`) provides a unified, reusable interface consumed by all four modules:

1. **Question 1 (Voice Qualification Agent)**:
   - Evaluates applicant business details against loan parameters.
   - Generates grounded answers by synthesizing RAG chunks retrieved from Q2.
   - Formats responses for speech synthesis.

2. **Question 2 (Production-Ready Knowledge Base)**:
   - Powers dense vector embeddings (`text-embedding-004` / `gemini-embedding-001`).
   - Evaluates search query relevance during hybrid retrieval benchmarks.

3. **Question 3 (Native-Language Voice Bots)**:
   - Handles natural SE Asian code-switching (Taglish in PH, Bahasa Indonesia in ID).
   - Generates culturally polite, localized financial responses without literal translation.

4. **Question 4 (Real-Time Live Call Insights)**:
   - Processes streaming transcript chunks in < 2 seconds.
   - Extracts real-time signals (compliance gaps, rising customer frustration, missed cross-sell opportunities).
