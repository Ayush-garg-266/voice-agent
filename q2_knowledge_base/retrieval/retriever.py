from typing import List, Dict, Tuple, Optional
from shared.logging import logger
from shared.llm.gemini_client import get_gemini_client
from q2_knowledge_base.chunking.chunker import KBChunk
from q2_knowledge_base.indexing.index_manager import ChromaVectorIndex, BM25SparseIndex
from q2_knowledge_base.reranking.reranker import CohereReranker
from q2_knowledge_base.citations.citation_generator import CitationGenerator
from shared.models import RetrievalResponse

from shared.config import settings

class KBRetrievalEngine:
    """
    Production-ready Hybrid Retrieval Engine for Q2 Knowledge Base.
    Combines ChromaDB vector similarity + BM25 keyword matching via Reciprocal Rank Fusion (RRF).
    Integrates optional Cohere Reranker, Safe Fallback, and Gemini Grounded Synthesis.
    """

    SAFE_FALLBACK_TEXT = (
        "I don't have enough verified information in the knowledge base to answer that reliably. "
        "I can connect you with a human representative."
    )

    def __init__(
        self,
        vector_index: Optional[ChromaVectorIndex] = None,
        bm25_index: Optional[BM25SparseIndex] = None,
        rrf_k: int = 60,
        score_threshold: Optional[float] = None
    ):
        self.vector_index = vector_index or ChromaVectorIndex()
        self.bm25_index = bm25_index or BM25SparseIndex()
        self.reranker = CohereReranker()
        self.citation_gen = CitationGenerator()
        self.gemini_client = get_gemini_client()
        self.rrf_k = rrf_k
        self.score_threshold = score_threshold if score_threshold is not None else settings.SUFFICIENCY_THRESHOLD

        # Chunk lookup map by chunk_id
        self.chunks_map: Dict[str, KBChunk] = {}

    def register_chunks(self, chunks: List[KBChunk]):
        for c in chunks:
            self.chunks_map[c.chunk_id] = c

    def get_chunk_by_record_id(self, record_id: str) -> Optional[KBChunk]:
        for c in self.chunks_map.values():
            if c.record_id == record_id:
                return c
        return None

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Tuple[KBChunk, float]]:
        """
        Executes Reciprocal Rank Fusion (RRF) combining dense vector and sparse BM25 scores.
        """
        # Fetch Top N from both indices
        fetch_n = max(top_k * 3, 15)
        vec_hits = self.vector_index.search(query, top_k=fetch_n)
        bm25_hits = self.bm25_index.search(query, top_k=fetch_n)

        rrf_scores: Dict[str, float] = {}

        # Accumulate Vector RRF scores
        for rank, (cid, score) in enumerate(vec_hits, start=1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Accumulate BM25 RRF scores
        for rank, (cid, score) in enumerate(bm25_hits, start=1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        if not rrf_scores:
            return []

        # Sort by RRF score descending
        sorted_cids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        max_rrf = sorted_cids[0][1] if sorted_cids else 1.0

        retrieved: List[Tuple[KBChunk, float]] = []
        candidate_chunks: List[KBChunk] = []
        candidate_scores: List[float] = []

        for cid, rrf_val in sorted_cids:
            if cid in self.chunks_map:
                chunk = self.chunks_map[cid]
                norm_score = rrf_val / max_rrf
                candidate_chunks.append(chunk)
                candidate_scores.append(norm_score)

        # Apply Optional Cohere Reranking if enabled
        if candidate_chunks:
            retrieved = self.reranker.rerank(query, candidate_chunks, top_k=top_k, scores=candidate_scores)

        return retrieved[:top_k]

    def query(self, query_text: str, top_k: int = 5) -> RetrievalResponse:
        """
        Full RAG Pipeline: Hybrid Search -> Sufficiency Check -> Gemini Synthesis -> Citations
        """
        retrieved = self.hybrid_search(query_text, top_k=top_k)

        # Sufficiency / Threshold Check: if no retrieved chunks or top relevance score below threshold
        if not retrieved or retrieved[0][1] < self.score_threshold:
            logger.info(f"Retrieval score below sufficiency threshold ({self.score_threshold}) for query '{query_text}'. Executing safe fallback.")
            return self.citation_gen.build_response(
                query=query_text,
                retrieved_chunks=retrieved,
                grounded_answer=self.SAFE_FALLBACK_TEXT,
                info_available=False
            )

        # Build grounded context prompt for Gemini
        context_blocks = []
        for idx, (chunk, score) in enumerate(retrieved, start=1):
            context_blocks.append(
                f"--- EVIDENCE CHUNK [{idx}] (Record ID: {chunk.record_id}, Source: {chunk.source_name}, Section: {chunk.section}) ---\n"
                f"{chunk.content}"
            )
        context_str = "\n\n".join(context_blocks)

        system_instruction = (
            "You are a strict, professional Business Loan Knowledge Base Assistant.\n"
            "Your task is to answer the user's query using ONLY the provided EVIDENCE CHUNKS below.\n"
            "STRICT RULES:\n"
            "1. Rely EXCLUSIVELY on facts explicitly stated in the evidence chunks.\n"
            "2. Do NOT invent, assume, or extrapolate policies, rates, or figures not in the text.\n"
            "3. If the evidence chunks do not contain enough information to answer reliably, respond exactly with:\n"
            f"'{self.SAFE_FALLBACK_TEXT}'\n"
            "4. Keep your answer clear, concise, direct, and professional."
        )

        user_prompt = (
            f"EVIDENCE CHUNKS:\n{context_str}\n\n"
            f"USER QUERY: {query_text}\n\n"
            f"Provide a grounded answer citing relevant facts:"
        )

        try:
            answer = self.gemini_client.generate(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=0.2
            )
            if not answer or self.SAFE_FALLBACK_TEXT.lower() in answer.lower():
                return self.citation_gen.build_response(
                    query=query_text,
                    retrieved_chunks=retrieved,
                    grounded_answer=self.SAFE_FALLBACK_TEXT,
                    info_available=False
                )

            return self.citation_gen.build_response(
                query=query_text,
                retrieved_chunks=retrieved,
                grounded_answer=answer.strip(),
                info_available=True
            )

        except Exception as e:
            logger.error(f"Error during Gemini grounded synthesis: {e}")
            return self.citation_gen.build_response(
                query=query_text,
                retrieved_chunks=retrieved,
                grounded_answer=self.SAFE_FALLBACK_TEXT,
                info_available=False
            )
