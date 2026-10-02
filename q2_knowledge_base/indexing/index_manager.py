import os
import shutil
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from rank_bm25 import BM25Okapi

from shared.config import settings
from shared.logging import logger
from shared.llm.gemini_client import get_gemini_client
from q2_knowledge_base.chunking.chunker import KBChunk

class ChromaVectorIndex:
    """
    ChromaDB vector store using Google Gemini Embeddings (gemini-embedding-001).
    Zero OpenAI dependencies.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = os.path.abspath(persist_dir or settings.CHROMA_PERSIST_DIR)
        os.makedirs(self.persist_dir, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "business_loan_kb"
        self.gemini_client = get_gemini_client()

    def _get_collection(self):
        return self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[KBChunk]):
        if not chunks:
            return

        collection = self._get_collection()
        documents = [c.content for c in chunks]
        ids = [c.chunk_id for c in chunks]
        metadatas = [
            {
                "record_id": c.record_id,
                "title": c.title,
                "category": c.category,
                "source_id": c.source_id,
                "source_name": c.source_name,
                "source_type": c.source_type,
                "version": c.version,
                "section": c.section,
                "created_at": c.created_at,
                "pii_flag": c.pii_flag
            }
            for c in chunks
        ]

        logger.info(f"Generating Gemini embeddings for {len(chunks)} chunk(s)...")
        embeddings = self.gemini_client.embed(documents, model="gemini-embedding-001")

        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(chunks)} chunks to ChromaDB collection '{self.collection_name}'")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Returns list of (chunk_id, cosine_similarity_score)
        """
        collection = self._get_collection()
        count = collection.count()
        if count == 0:
            return []

        query_embedding = self.gemini_client.embed(query, model="gemini-embedding-001")[0]
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, count)
        )

        hits = []
        if results and results["ids"] and results["ids"][0]:
            chunk_ids = results["ids"][0]
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(chunk_ids)

            for cid, dist in zip(chunk_ids, distances):
                similarity = max(0.0, 1.0 - dist)
                hits.append((cid, similarity))

        return hits

    def reset(self):
        try:
            self.chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._get_collection()


class BM25SparseIndex:
    """
    Rank-BM25 sparse keyword search index.
    """

    def __init__(self):
        self.chunks: List[KBChunk] = []
        self.chunk_ids: List[str] = []
        self.bm25: Optional[BM25Okapi] = None

    def build_index(self, chunks: List[KBChunk]):
        self.chunks = chunks
        self.chunk_ids = [c.chunk_id for c in chunks]

        corpus = [c.content.lower().split() for c in chunks]
        if corpus:
            self.bm25 = BM25Okapi(corpus)
            logger.info(f"BM25 index built with {len(chunks)} chunks.")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        if not self.bm25 or not self.chunk_ids:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        top_hits = indexed_scores[:top_k]
        max_score = top_hits[0][1] if top_hits and top_hits[0][1] > 0 else 1.0

        hits = []
        for idx, raw_score in top_hits:
            if raw_score > 0:
                cid = self.chunk_ids[idx]
                norm_score = raw_score / max_score
                hits.append((cid, norm_score))

        return hits
