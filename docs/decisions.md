# Architectural & Design Decisions Record (ADR)

## ADR-001: Strict Standardisation on Google Gemini API (`google-genai`)

- **Context**: The project requires AI reasoning across voice agent turn-taking, RAG synthesis, multilingual translation, and real-time signal extraction.
- **Decision**: Standardize 100% of LLM capabilities on Google's official `google-genai` Python SDK.
- **Rationale**: Complies with strict constraint prohibiting OpenAI dependencies. Gemini Flash offers sub-second inference latencies required for real-time nudges (Q4) and voice tool execution (Q1).
- **Consequences**: All model calls use `google-genai`. API keys strictly sourced from `GEMINI_API_KEY` in `.env`.

---

## ADR-002: Hybrid Sparse-Dense Retrieval for Business Loan Knowledge Base

- **Context**: Q2 Knowledge Base must retrieve precise policy constraints (e.g. "$100,000 revenue requirement", "LLC registration rule") while also handling natural language semantic queries ("Can a new company get funded?").
- **Decision**: Combine ChromaDB (Dense Vector Search) with `rank_bm25` (Sparse Keyword Search) using Reciprocal Rank Fusion (RRF).
- **Rationale**: Pure vector search often misses exact numerical thresholds or legal code references. BM25 guarantees keyword match accuracy, while vectors provide semantic flexibility.

---

## ADR-003: Separation of Qualification Engine from Knowledge Retrieval

- **Context**: Q1 voice agent prompt could easily become bloated if all FAQs, objections, and interest tables are embedded into system instructions.
- **Decision**: Enforce strict tool calling (`query_knowledge_base`) for all policy questions. System prompt retains only step-by-step qualification flow states.
- **Rationale**: Keeps prompt footprint minimal, reduces hallucination risk, ensures policy updates in Q2 immediately reflect in Q1 without prompt re-engineering.

---

## ADR-004: Dual Real-Time Audio Engine (Live WebRTC + Real-Time Chunk Replayer)

- **Context**: Q4 requires analyzing calls while happening. Testing real-time audio requires a reliable, reproducible mechanism.
- **Decision**: Implement both a live WebSocket audio receiver and a deterministic real-time audio chunk replayer.
- **Rationale**: Allows automated benchmark testing of P50/P95 latency without needing a human to dial in for every test cycle.
