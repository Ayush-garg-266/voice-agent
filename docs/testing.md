# Evaluation and Testing Methodology

## 1. Scope & Strategy

Testing and evaluation across the four modules must be empirical, deterministic, and verifiable. No metrics or results will be fabricated.

---

## 2. Question 1 — Voice Agent Test Coverage

The Q1 voice agent will be evaluated against five explicit test scripts:

1. **Test-Q1-01 (Cooperative Qualification)**:
   - *Input*: Valid business owner, 3 years in business, $250k revenue, seeking $50k loan.
   - *Expected Outcome*: Completes qualification, marks lead eligible, triggers CRM callback webhook.

2. **Test-Q1-02 (Objection Handling)**:
   - *Input*: Asks why personal guarantee is required and challenges interest rates.
   - *Expected Outcome*: Bot invokes `query_knowledge_base`, cites section 3.2 policy, explains risk model without hallucinating.

3. **Test-Q1-03 (Conflicting Details)**:
   - *Input*: Claims $500k annual revenue but later states $10k monthly revenue ($120k/yr).
   - *Expected Outcome*: Bot identifies discrepancy, politely asks for clarification.

4. **Test-Q1-04 (Out-of-Scope Fallback)**:
   - *Input*: Asks how to file tax returns or for personal mortgage advice.
   - *Expected Outcome*: Bot executes safe fallback: "I am trained only to assist with business loan qualification..."

5. **Test-Q1-05 (Human Escalation Request)**:
   - *Input*: Demands to speak with a human agent immediately.
   - *Expected Outcome*: Bot invokes human transfer webhook and confirms agent callback.

---

## 3. Question 2 — Knowledge Base Retrieval Benchmark

Evaluation script `scripts/evaluate_retrieval.py` will run 5 standard queries against Q2 and measure:
- Hit Rate @ K=3
- Reciprocal Rank (MRR)
- Citation Accuracy (Source & Section verification)
- Response Verdict: Correct / Partially Correct / Incorrect

---

## 4. Question 3 — Multilingual Localization Evaluation

Evaluates Philippines (Taglish) and Indonesia (Bahasa) bots across:
- **Code-Switching Smoothness**: No awkward literal grammar translations.
- **Honorific / Politeness Accuracy**: Proper placement of *po/opo* (PH) and *Bapak/Ibu* (ID).
- **Fallback Integrity**: Graceful fallback in native language when out-of-scope question occurs.

---

## 5. Question 4 — Real-Time Nudge & Latency Benchmark

Simulation script `scripts/run_q4_simulation.py` replays pre-recorded audio calls and measures:
- P50 & P95 end-to-end latency (ASR -> Gemini Signal Extraction -> WebSocket broadcast).
- False Positive Rate under noisy audio conditions.
- Suppression Verification: Ensures identical nudges are not spammed within the 15-second cooldown window.
