# Production Plan & Roadmap

## 1. Production Architecture Evolution

Moving from local prototype to high-scale production deployment involves upgrading storage, hosting, and streaming infrastructure.

```
[Local Prototype]                        [Production Deployment]
- SQLite                                 -> Managed PostgreSQL (Cloud SQL / RDS)
- Local ChromaDB                         -> ChromaDB Distributed / Pinecone / Milvus
- In-Memory WebSockets                   -> Redis Pub/Sub + API Gateway WebSockets
- Single Uvicorn Process                 -> Kubernetes (GKE / EKS) Auto-scaled Deployment
```

---

## 2. Infrastructure & Scalability Plan

### Database & Vector Storage Migration
- **Relational DB**: Migrate from SQLite to PostgreSQL with SQLAlchemy / AsyncPG connection pooling.
- **Vector Storage**: Persist vector indexes to managed cloud storage or containerized ChromaDB instances with read replicas.

### Real-Time Signal Scaling (Q4 at 10x - 100x Scale)
- **Concurrency Bottleneck**: LLM inference latency for real-time signals when handling 100+ concurrent calls.
- **Mitigation Strategy**:
  1. **Sliding Window Filtering**: Only send audio transcripts to Gemini when transcript content changes significantly (VAD + Lexical delta trigger).
  2. **Model Tiering**: Use lightweight Gemini Flash models for signal extraction, deferring complex summarization to async worker tasks.
  3. **Event-Driven Redis Pipeline**: Decouple ASR ingestion from LLM signal extraction using Redis Streams.

---

## 3. Security, Compliance & PII Strategy

1. **PII Masking at Ingestion**: All incoming user inputs (names, tax IDs, phone numbers, email addresses) pass through an automated regex + NER redaction filter before vector embedding or LLM context insertion.
2. **Key & Secret Management**: API keys managed via AWS Secrets Manager / GCP Secret Manager. Zero local `.env` storage in production.
3. **Audit Logging**: Structured JSON logging with trace IDs mapped across Q1-Q4 calls for full compliance traceability.
