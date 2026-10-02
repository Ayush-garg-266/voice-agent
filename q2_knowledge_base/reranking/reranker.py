import os
import httpx
from typing import List, Tuple, Optional
from shared.config import settings
from shared.logging import logger
from q2_knowledge_base.chunking.chunker import KBChunk

class CohereReranker:
    """
    Optional Cohere Rerank integration.
    Gracefully falls back to original RRF ranks if COHERE_API_KEY is not configured or fails.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.COHERE_API_KEY or os.getenv("COHERE_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("cohere_API_KEY"))

    def rerank(self, query: str, chunks: List[KBChunk], top_k: int = 5, scores: Optional[List[float]] = None) -> List[Tuple[KBChunk, float]]:
        if not self.is_available() or not chunks:
            logger.debug("Cohere API key not available or invalid; returning original hybrid ranking.")
            if scores and len(scores) == len(chunks):
                return [(c, s) for c, s in zip(chunks[:top_k], scores[:top_k])]
            return [(c, 1.0 - (idx * 0.05)) for idx, c in enumerate(chunks[:top_k])]

        try:
            logger.info("Executing Cohere Rerank API call...")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            documents = [c.content for c in chunks]
            payload = {
                "model": "rerank-english-v3.0",
                "query": query,
                "documents": documents,
                "top_n": min(top_k, len(chunks))
            }

            with httpx.Client(timeout=5.0) as client:
                resp = client.post("https://api.cohere.com/v1/rerank", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    reranked = []
                    for res in data.get("results", []):
                        idx = res["index"]
                        score = float(res["relevance_score"])
                        reranked.append((chunks[idx], score))
                    return reranked
                else:
                    logger.warning(f"Cohere Rerank API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Cohere Rerank API call failed: {e}. Falling back to RRF ranking.")

        if scores and len(scores) == len(chunks):
            return [(c, s) for c, s in zip(chunks[:top_k], scores[:top_k])]
        return [(c, 1.0 - (idx * 0.05)) for idx, c in enumerate(chunks[:top_k])]
