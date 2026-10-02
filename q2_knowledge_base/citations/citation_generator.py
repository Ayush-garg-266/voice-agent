from typing import List, Dict, Any
from shared.models import RetrievalCitation, RetrievalResponse
from q2_knowledge_base.chunking.chunker import KBChunk

class CitationGenerator:
    """
    Formats traceable citations from retrieved Knowledge Base chunks.
    Ensures every response clearly attributes source document, section, version, and record ID.
    """

    @staticmethod
    def format_citation(chunk: KBChunk, score: float) -> RetrievalCitation:
        sec_info = f" > {chunk.section}" if chunk.section else ""
        citation_str = f"[{chunk.source_name}{sec_info} (v{chunk.version}, ID: {chunk.record_id})]"

        # Snippet preview (first 200 chars)
        snippet = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content

        return RetrievalCitation(
            record_id=chunk.record_id,
            source_document=chunk.source_name,
            section=chunk.section,
            content_snippet=snippet,
            relevance_score=round(score, 4)
        )

    def build_response(
        self,
        query: str,
        retrieved_chunks: List[tuple[KBChunk, float]],
        grounded_answer: str,
        info_available: bool = True
    ) -> RetrievalResponse:
        citations = [
            self.format_citation(chunk, score)
            for chunk, score in retrieved_chunks
        ]
        return RetrievalResponse(
            query=query,
            citations=citations,
            grounded_answer=grounded_answer,
            info_available=info_available
        )
