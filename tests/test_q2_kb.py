import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from q2_knowledge_base.ingestion.loader import DocumentLoader, RawDocument
from q2_knowledge_base.cleaning.cleaner import TextCleaner, Deduplicator
from q2_knowledge_base.pii.pii_scrubber import PIIScrubber
from q2_knowledge_base.chunking.chunker import SemanticChunker, KBChunk
from q2_knowledge_base.indexing.index_manager import ChromaVectorIndex, BM25SparseIndex
from q2_knowledge_base.retrieval.retriever import KBRetrievalEngine
from q2_knowledge_base.citations.citation_generator import CitationGenerator
from q2_knowledge_base.api.app import app, run_ingestion_pipeline

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "q2_knowledge_base", "data", "raw"))

def test_document_loader():
    loader = DocumentLoader(RAW_DIR)
    docs = loader.load_all()
    assert len(docs) >= 5, "Expected at least 5 raw documents to be loaded."
    for doc in docs:
        assert doc.source_id, "Source ID missing"
        assert doc.source_name, "Source name missing"
        assert doc.source_type, "Source type missing"

def test_text_cleaner():
    cleaner = TextCleaner()
    raw_text = "Header  \n\n\n\nDate:  2024/05/12  \n  annual turnover of $100k "
    cleaned = cleaner.clean_text(raw_text)
    assert "\n\n\n" not in cleaned
    assert "2024-05-12" in cleaned
    assert "revenue (turnover)" in cleaned

def test_deduplicator():
    dedup = Deduplicator(similarity_threshold=0.75)
    text1 = "Unsecured business loan minimum revenue requirement is $100,000 USD per year."
    text2 = "Unsecured business loan minimum revenue requirement is $100,000 USD per year."
    text3 = "Unsecured business loan minimum revenue requirement is $100,000 USD annually."

    assert not dedup.is_exact_duplicate(text1)
    assert dedup.is_exact_duplicate(text2)

    is_near, sim, match_id = dedup.is_near_duplicate("doc_1", text1)
    is_near2, sim2, match_id2 = dedup.is_near_duplicate("doc_3", text3)
    assert is_near2, f"Expected near-duplicate detection between text1 and text3, got sim={sim2}"
    assert sim2 >= 0.75

def test_pii_scrubber():
    scrubber = PIIScrubber()
    sample = "Contact John Doe at john.doe@demobusiness.local or call 555-123-4567. EIN: 12-3456789."
    scrubbed, pii_detected = scrubber.scrub(sample)
    assert pii_detected
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed
    assert "[REDACTED_TAX_ID]" in scrubbed

def test_semantic_chunker():
    raw_doc = RawDocument(
        content="# Section 1\nThis is test policy content for business loans.\n\n## Section 2\nMore detailed eligibility rules here.",
        source_id="SRC_TEST",
        source_name="test_doc.md",
        source_type="markdown",
        version="1.0",
        category="policy"
    )
    chunker = SemanticChunker(target_chunk_size=100)
    chunks = chunker.chunk_document(raw_doc)
    assert len(chunks) >= 2
    assert chunks[0].source_id == "SRC_TEST"
    assert chunks[0].section == "Section 1"
    assert chunks[1].section == "Section 2"

def test_retrieval_and_safe_fallback():
    chunk1 = KBChunk(
        record_id="kb_test_001",
        chunk_id="chunk_test_001",
        title="Unsecured Loan Policy",
        category="qualification",
        source_id="SRC_TEST",
        source_name="test_policy.md",
        source_type="markdown",
        version="2.0",
        section="Eligibility",
        content="To qualify for an unsecured business loan, the applicant enterprise must demonstrate at least $100,000 in gross annual revenue.",
        created_at="2026-01-15"
    )

    vec_idx = ChromaVectorIndex()
    bm25_idx = BM25SparseIndex()
    engine = KBRetrievalEngine(vector_index=vec_idx, bm25_index=bm25_idx, score_threshold=0.01)

    all_chunks = [chunk1]
    vec_idx.reset()
    vec_idx.add_chunks(all_chunks)
    bm25_idx.build_index(all_chunks)
    engine.register_chunks(all_chunks)

    # Valid Query Test
    res = engine.query("What is the minimum annual revenue for an unsecured business loan?")
    assert len(res.citations) > 0 or res.info_available

    # Out-of-Scope Query Safe Fallback Test
    fallback_res = engine.query("How do I file my personal income tax return in Texas?")
    assert not fallback_res.info_available or "don't have enough verified information" in fallback_res.grounded_answer.lower()

@pytest.fixture(scope="module", autouse=True)
def setup_kb_data():
    run_ingestion_pipeline()

def test_strongly_supported_query_grounded_answer():
    client = TestClient(app)
    query_payload = {"query": "What are the eligibility requirements for a business loan?", "top_k": 5}
    res = client.post("/kb/query", json=query_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["info_available"] is True
    assert "don't have enough verified information" not in data["grounded_answer"].lower()
    assert len(data["citations"]) > 0
    top_cit = data["citations"][0]
    assert top_cit["record_id"]
    assert top_cit["source_document"]
    assert top_cit["relevance_score"] > 0.0

def test_genuinely_unsupported_query_safe_fallback():
    client = TestClient(app)
    query_payload = {"query": "How do I bake a chocolate cake at home?", "top_k": 5}
    res = client.post("/kb/query", json=query_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["info_available"] is False
    assert "don't have enough verified information" in data["grounded_answer"].lower()

def test_weak_ambiguous_retrieval_safe_fallback():
    vec_idx = ChromaVectorIndex()
    bm25_idx = BM25SparseIndex()
    # High threshold ensures weak candidate retrieval triggers fallback
    engine = KBRetrievalEngine(vector_index=vec_idx, bm25_index=bm25_idx, score_threshold=0.9999)
    loader = DocumentLoader(RAW_DIR)
    chunker = SemanticChunker()
    docs = loader.load_all()
    chunks = []
    for doc in docs:
        chunks.extend(chunker.chunk_document(doc))
    engine.register_chunks(chunks)
    bm25_idx.build_index(chunks)

    res = engine.query("What is the processing fee for a business loan?")
    # Since top relevance score is below 0.9999 threshold, must execute safe fallback
    assert res.info_available is False
    assert "don't have enough verified information" in res.grounded_answer.lower()
    assert len(res.citations) > 0  # Citations remain attached

def test_citations_remain_attached_to_answers():
    client = TestClient(app)
    query_payload = {"query": "What are the eligibility requirements for a business loan?", "top_k": 3}
    res = client.post("/kb/query", json=query_payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["citations"]) > 0
    for citation in data["citations"]:
        assert "record_id" in citation
        assert "source_document" in citation
        assert "relevance_score" in citation

def test_api_endpoints():
    client = TestClient(app)

    # Health check
    res = client.get("/kb/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # Query endpoint
    query_payload = {"query": "What is the processing fee for a business loan?", "top_k": 3}
    res_q = client.post("/kb/query", json=query_payload)
    assert res_q.status_code == 200
    data = res_q.json()
    assert "grounded_answer" in data
    assert "citations" in data
