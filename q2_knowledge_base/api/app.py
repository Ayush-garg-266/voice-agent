import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from shared.logging import logger
from q2_knowledge_base.ingestion.loader import DocumentLoader
from q2_knowledge_base.chunking.chunker import SemanticChunker, KBChunk
from q2_knowledge_base.indexing.index_manager import ChromaVectorIndex, BM25SparseIndex
from q2_knowledge_base.retrieval.retriever import KBRetrievalEngine
from shared.models import RetrievalResponse

# Initialize FastAPI application
app = FastAPI(
    title="Q2 Production-Ready Knowledge Base API",
    description="Canonical RAG Knowledge Base API powering Business Loan Voice Qualification & Insights",
    version="1.0.0"
)

# Global singleton instances for API worker
RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw"))

loader = DocumentLoader(RAW_DATA_DIR)
chunker = SemanticChunker()
vector_index = ChromaVectorIndex()
bm25_index = BM25SparseIndex()
retrieval_engine = KBRetrievalEngine(vector_index=vector_index, bm25_index=bm25_index)

all_chunks: List[KBChunk] = []

def run_ingestion_pipeline() -> Dict[str, Any]:
    global all_chunks
    logger.info("Starting Knowledge Base Ingestion & Indexing Pipeline...")
    raw_docs = loader.load_all()

    chunks_list: List[KBChunk] = []
    for doc in raw_docs:
        doc_chunks = chunker.chunk_document(doc)
        chunks_list.extend(doc_chunks)

    # Reset vector index and add chunks
    vector_index.reset()
    vector_index.add_chunks(chunks_list)

    # Build BM25 index
    bm25_index.build_index(chunks_list)

    # Register chunks with retrieval engine
    retrieval_engine.register_chunks(chunks_list)
    all_chunks = chunks_list

    return {
        "status": "success",
        "documents_ingested": len(raw_docs),
        "chunks_indexed": len(chunks_list)
    }

# Execute initial ingestion at startup
@app.on_event("startup")
def startup_event():
    try:
        run_ingestion_pipeline()
    except Exception as e:
        logger.error(f"KB Startup Ingestion failed: {e}")


# Request Models
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


# API Endpoints
@app.get("/kb/health")
def health_check():
    return {
        "status": "healthy",
        "module": "Q2 Knowledge Base",
        "total_chunks_loaded": len(all_chunks),
        "vector_index_status": "active",
        "bm25_index_status": "active"
    }


@app.post("/kb/ingest")
def trigger_ingestion():
    try:
        res = run_ingestion_pipeline()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/kb/reindex")
def trigger_reindex():
    return trigger_ingestion()


@app.post("/kb/query", response_model=RetrievalResponse)
def query_knowledge_base(request: QueryRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    try:
        res = retrieval_engine.query(request.query, top_k=request.top_k or 5)
        return res
    except Exception as e:
        logger.error(f"Query endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval query failed: {str(e)}")


@app.get("/kb/records/{record_id}")
def get_record_by_id(record_id: str):
    chunk = retrieval_engine.get_chunk_by_record_id(record_id)
    if not chunk:
        raise HTTPException(status_code=404, detail=f"Record ID '{record_id}' not found.")
    return chunk.to_dict()
