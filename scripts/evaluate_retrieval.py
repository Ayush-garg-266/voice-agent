#!/usr/bin/env python3
"""
Q2 Knowledge Base Retrieval Benchmark & Evaluation Harness.
Evaluates 5 distinct retrieval test cases covering:
1. Business-loan eligibility requirements
2. Required documentation
3. Loan amount / qualification rule
4. An objection or FAQ
5. An unsupported/out-of-scope question
"""

import sys
import os
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from q2_knowledge_base.ingestion.loader import DocumentLoader
from q2_knowledge_base.chunking.chunker import SemanticChunker
from q2_knowledge_base.indexing.index_manager import ChromaVectorIndex, BM25SparseIndex
from q2_knowledge_base.retrieval.retriever import KBRetrievalEngine

RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "q2_knowledge_base", "data", "raw"))

# 5 Mandatory Evaluation Benchmark Queries
EVALUATION_QUERIES = [
    {
        "id": "EVAL_001",
        "category": "Business-loan eligibility requirements",
        "question": "What are the eligibility requirements for a business loan?",
        "expected_sources": ["product_guidelines_v2.md", "qualification_rules_form.json"],
        "expect_supported": True
    },
    {
        "id": "EVAL_002",
        "category": "Required documentation",
        "question": "What documentation is required to apply for a business loan?",
        "expected_sources": ["product_guidelines_v2.md", "qualification_rules_form.json", "objection_handling_guide.md"],
        "expect_supported": True
    },
    {
        "id": "EVAL_003",
        "category": "Loan amount / qualification rule",
        "question": "What is the maximum loan amount for unsecured business loans and minimum turnover?",
        "expected_sources": ["product_guidelines_v2.md", "product_matrix.csv", "product_policy_v1_legacy.md"],
        "expect_supported": True
    },
    {
        "id": "EVAL_004",
        "category": "An objection or FAQ",
        "question": "Why do you need so many business documents? I don't want to provide all of them.",
        "expected_sources": ["objection_handling_guide.md", "escalation_and_edge_cases.md", "faq_webpage.html"],
        "expect_supported": True
    },
    {
        "id": "EVAL_005",
        "category": "An unsupported/out-of-scope question",
        "question": "How do I bake a chocolate cake at home?",
        "expected_sources": ["none"],
        "expect_supported": False
    }
]

def main():
    print("=" * 75)
    print("  Q2 Knowledge Base Retrieval Benchmark & Citation Evaluation")
    print("=" * 75)

    print("[*] Ingesting and indexing raw knowledge base files...")
    loader = DocumentLoader(RAW_DATA_DIR)
    chunker = SemanticChunker()
    vector_index = ChromaVectorIndex()
    bm25_index = BM25SparseIndex()
    engine = KBRetrievalEngine(vector_index=vector_index, bm25_index=bm25_index)

    raw_docs = loader.load_all()
    all_chunks = []
    for doc in raw_docs:
        all_chunks.extend(chunker.chunk_document(doc))

    vector_index.reset()
    vector_index.add_chunks(all_chunks)
    bm25_index.build_index(all_chunks)
    engine.register_chunks(all_chunks)

    print(f"[*] Benchmark initialized: {len(all_chunks)} chunks indexed across {len(raw_docs)} documents.")
    print("-" * 75)

    results = []

    for item in EVALUATION_QUERIES:
        qid = item["id"]
        cat = item["category"]
        qtext = item["question"]
        exp_sources = item["expected_sources"]
        expect_supported = item["expect_supported"]

        print(f"\n[{qid}] Category: {cat}")
        print(f"Query: \"{qtext}\"")

        res = engine.query(qtext, top_k=5)

        retrieved_src = "None"
        retrieved_chunk_id = "None"
        section_info = "None"
        top_score = 0.0

        if res.citations:
            top_cit = res.citations[0]
            retrieved_src = top_cit.source_document
            retrieved_chunk_id = top_cit.record_id
            section_info = top_cit.section or "General"
            top_score = top_cit.relevance_score

        # Determine empirical verdict
        if expect_supported:
            is_match = any(exp_src.lower() in retrieved_src.lower() for exp_src in exp_sources)
            if is_match and res.info_available:
                verdict = "PASS"
                explanation = f"Retrieved relevant chunk from {retrieved_src} [{section_info}] with score {top_score:.4f}. Grounded answer generated."
            else:
                verdict = "FAIL"
                explanation = f"Failed to retrieve expected source {exp_sources} or info_available was False."
        else:
            if not res.info_available or "don't have enough verified information" in res.grounded_answer.lower():
                verdict = "PASS"
                explanation = "Correctly recognized unsupported query and executed safe fallback without inventing facts."
            else:
                verdict = "FAIL"
                explanation = "Invented an answer for an out-of-scope question."

        print(f"  -> Expected Sources: {exp_sources}")
        print(f"  -> Top Chunk / ID:   {retrieved_chunk_id} ({retrieved_src})")
        print(f"  -> Section Info:     {section_info}")
        print(f"  -> Relevance Score:  {top_score:.4f}")
        print(f"  -> Info Available:   {res.info_available}")
        print(f"  -> Verdict:          [{verdict}]")
        print(f"  -> Relevance Reason: {explanation}")
        print(f"  -> Grounded Answer:  \"{res.grounded_answer[:150]}...\"")

        results.append({
            "eval_id": qid,
            "category": cat,
            "user_question": qtext,
            "top_retrieved_chunk_id": retrieved_chunk_id,
            "source_document": retrieved_src,
            "section_info": section_info,
            "relevance_score": top_score,
            "relevance_explanation": explanation,
            "verdict": verdict,
            "info_available": res.info_available,
            "grounded_answer": res.grounded_answer,
            "citations": [c.model_dump() for c in res.citations]
        })

    pass_count = sum(1 for r in results if r["verdict"] == "PASS")
    fail_count = sum(1 for r in results if r["verdict"] == "FAIL")

    print("\n" + "=" * 75)
    print("  Q2 Retrieval Benchmark Summary Report:")
    print("=" * 75)
    print(f"Total Evaluated Queries: {len(EVALUATION_QUERIES)}")
    print(f"Passed:                {pass_count} ({pass_count/len(EVALUATION_QUERIES)*100:.1f}%)")
    print(f"Failed:                {fail_count}")
    print("=" * 75 + "\n")

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "recordings"))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "retrieval_benchmark_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[SUCCESS] Benchmark results saved to {out_file}")

if __name__ == "__main__":
    main()
