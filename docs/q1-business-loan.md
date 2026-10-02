# Question 1 — Knowledge-Grounded Business Loan Qualification Voice Agent

## 1. Executive Summary

Question 1 implements a working **Knowledge-Grounded Business Loan Qualification Voice Agent**.

The system prompt contains **zero hardcoded business policies, interest rates, or eligibility rules**. All business facts are retrieved dynamically from the **Q2 Knowledge Base** via the `query_knowledge_base` RAG tool.

---

## 2. Conversation Flow & Qualification Logic

1. **Greeting & Purpose**: Explains purpose concisely to establish trust.
2. **Gradual Collection**: Collects Business Name, Entity Type, Operating History, Annual Revenue, Monthly Cashflow, Requested Loan Amount, Purpose, and Preferred Tenor.
3. **Q2 RAG Integration**: Calls `query_knowledge_base` whenever the caller asks about rates, document requirements, fees, or raises objections.
4. **Edge Cases**: Detects incomplete or conflicting revenue details ($500k annual vs $10k monthly) and asks for clarification.
5. **Out-of-Scope Fallback**: States verified information is unavailable and offers human representative handoff.
6. **Human Escalation**: Stops persuasion immediately when a human is requested, sets `escalation_required=True`, and provides a polite transfer message.

---

## 3. Structured Internal Output Schema

At the end of each turn, the qualification engine outputs internal structured data:

```json
{
  "qualification_status": "prequalified",
  "missing_information": [],
  "collected_information": {
    "business_name": "Nexus Technology LLC",
    "operating_months": 36,
    "annual_revenue": 250000.0,
    "requested_amount": 50000.0
  },
  "retrieved_evidence": [
    {
      "record_id": "kb_src_doc_001_004",
      "source_document": "product_guidelines_v2.md",
      "relevance_score": 0.9996
    }
  ],
  "next_step": "Issue preliminary conditional pre-qualification and trigger digital document upload link.",
  "escalation_required": false
}
```

---

## 4. Test Scenarios & Benchmark Results

Automated test suite (`q1_business_loan/tests/test_q1_agent.py`) executes 5 mandatory call scenarios:

- **TEST 1 (Cooperative Customer)**: `PASSED` -> Status: `prequalified`.
- **TEST 2 (Interest Rate Objection)**: `PASSED` -> Triggers Q2 RAG tool & returns grounded unsecured risk explanation.
- **TEST 3 (Conflicting Business Details)**: `PASSED` -> Status: `needs_review` due to $500k vs $10k monthly discrepancy.
- **TEST 4 (Out-of-Scope Question)**: `PASSED` -> Returns safe fallback response for personal mortgage tax deduction question.
- **TEST 5 (Human Escalation Request)**: `PASSED` -> Status: `escalated`, `escalation_required=True`.

Transcripts saved to [`q1_business_loan/evaluation/transcripts/`](file:///C:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/evaluation/transcripts/).
