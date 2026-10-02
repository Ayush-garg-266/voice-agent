from typing import Dict, Any, Optional
from shared.logging import logger
from q2_knowledge_base.retrieval.retriever import KBRetrievalEngine
from q2_knowledge_base.indexing.index_manager import ChromaVectorIndex, BM25SparseIndex

import os
from q2_knowledge_base.ingestion.loader import DocumentLoader
from q2_knowledge_base.chunking.chunker import SemanticChunker

# Initialize singleton retrieval engine for Q1 agent tool
_retrieval_engine: Optional[KBRetrievalEngine] = None

def get_retrieval_engine() -> KBRetrievalEngine:
    global _retrieval_engine
    if _retrieval_engine is None:
        vec_idx = ChromaVectorIndex()
        bm25_idx = BM25SparseIndex()
        _retrieval_engine = KBRetrievalEngine(vector_index=vec_idx, bm25_index=bm25_idx)

        # Load raw documents and register chunks to ensure full hybrid RRF & metadata mapping
        raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "q2_knowledge_base", "data", "raw"))
        if os.path.exists(raw_dir):
            try:
                loader = DocumentLoader(raw_dir)
                chunker = SemanticChunker()
                raw_docs = loader.load_all()
                chunks = []
                for doc in raw_docs:
                    chunks.extend(chunker.chunk_document(doc))
                bm25_idx.build_index(chunks)
                _retrieval_engine.register_chunks(chunks)
            except Exception as e:
                logger.error(f"Failed to populate chunks in Q1 KB tool: {e}")

    return _retrieval_engine


def query_knowledge_base(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    RAG Tool called by Q1 Voice Agent whenever a business policy, interest rate,
    eligibility rule, or objection question is raised.

    Args:
        query: The question or objection string from the caller.
        top_k: Number of relevant evidence chunks to retrieve.

    Returns:
        Dict containing grounded_answer, info_available flag, and traceable citations.
    """
    logger.info(f"Q1 RAG Tool execution for query: '{query}'")
    try:
        engine = get_retrieval_engine()
        res = engine.query(query_text=query, top_k=top_k)
        return res.model_dump()
    except Exception as e:
        logger.error(f"Error executing Q1 RAG tool: {e}")
        return {
            "query": query,
            "info_available": False,
            "grounded_answer": "I don't have enough verified information in the knowledge base to answer that reliably. I can connect you with a human representative.",
            "citations": []
        }


# Vapi Function Call Specification
VAPI_KB_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "query_knowledge_base",
        "description": "Retrieves verified business loan policies, interest rates, eligibility criteria, and objection handling scripts from Q2 Knowledge Base.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The customer's question or objection regarding business loans."
                }
            },
            "required": ["query"]
        }
    }
}
