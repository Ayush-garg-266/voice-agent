# Q1 — Knowledge-Grounded Business Loan Qualification Voice Agent

This module implements the functional voice agent prototype for **Business-Loan Qualification**.

## 1. Architecture Overview

```
[Caller / Web Simulator / Vapi Phone]
                 │
                 ▼ (Voice Audio / Webhook Event)
   [Vapi Platform / Web Simulator UI]
                 │
                 ▼ (HTTP POST /q1/webhook or /q1/qualify)
  [Q1 FastAPI Server & Conversation Manager]
                 │
  ┌──────────────┴──────────────┐
  ▼                             ▼
[Q1 Qualification Engine]    [Q2 Knowledge Base RAG Tool]
(Evaluates revenue, age,     (POST /kb/query via ChromaDB +
 amount, cashflow, rules)     BM25 RRF Hybrid Index)
```

---

## 2. Directory Structure

- `agent/`:
  - `qualification_engine.py`: Qualification rules, state evaluation, structured output generator.
  - `conversation_manager.py`: Stateful conversation manager interpreting user turns.
- `prompts/`:
  - `system_prompt.py`: Gemini system prompt (role, safety rules, fallback, escalation).
- `tools/`:
  - `kb_tool.py`: RAG tool connecting Q1 to Q2 (`query_knowledge_base`).
- `webhooks/`:
  - `vapi_webhook.py`: FastAPI routes for Vapi server webhooks, REST qualification, health check, and session logs.
  - `simulator.html`: Interactive web browser simulator interface.
- `evaluation/`:
  - `test_scenarios.json`: 5 benchmark test scenarios.
  - `transcripts/`: Sanitized transcript logs generated from automated test runs.
- `tests/`:
  - `test_q1_agent.py`: Automated pytest test suite executing all 5 scenarios.

---

## 3. Running Automated Tests & Web Simulator

```bash
# Run automated test suite (Executes 5 test scenarios)
pytest q1_business_loan/tests/test_q1_agent.py -v

# Start FastAPI server
python -m uvicorn q1_business_loan.webhooks.vapi_webhook:app --host 0.0.0.0 --port 8001
```

Access the Web Simulator UI / health check at `http://localhost:8001/q1/health`.
