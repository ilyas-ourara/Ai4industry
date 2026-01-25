"""
FastAPI Backend for RAG Multi-Agent Application.
Provides REST API endpoints to connect the Next.js frontend to the RAG system.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO",
)
logger.add(
    "logs/api.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)



class QuestionRequest(BaseModel):
    """Request model for asking a question."""
    question: str = Field(..., min_length=1, description="La question de l'utilisateur")


class Citation(BaseModel):
    """Citation/source reference."""
    content: str = Field(..., description="Extrait du texte source")
    source: str = Field(..., description="Nom du document source")
    page: Optional[int] = Field(default=None, description="Numéro de page")
    relevance_score: Optional[float] = Field(default=None, description="Score de pertinence")


class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    answer: str = Field(..., description="La réponse générée par le RAG")
    sources: List[str] = Field(default_factory=list, description="Liste des sources utilisées")
    citations: List[Citation] = Field(default_factory=list, description="Citations détaillées")
    confidence: Optional[float] = Field(default=None, description="Score de confiance")
    processing_time: Optional[float] = Field(default=None, description="Temps de traitement en secondes")


class SearchRequest(BaseModel):
    """Request model for document search."""
    query: str = Field(..., min_length=1, description="La requête de recherche")
    top_k: int = Field(default=5, ge=1, le=20, description="Nombre de résultats")


class SearchResult(BaseModel):
    """Individual search result."""
    content: str = Field(..., description="Contenu du chunk")
    source: str = Field(..., description="Document source")
    score: float = Field(..., description="Score de pertinence")
    page: Optional[int] = Field(default=None, description="Numéro de page")


class SearchResponse(BaseModel):
    """Response model for the /search endpoint."""
    results: List[SearchResult] = Field(default_factory=list)
    total: int = Field(default=0, description="Nombre total de résultats")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    indexed: bool = Field(default=False)
    documents_count: int = Field(default=0)
    chunks_count: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.now)


class StatusResponse(BaseModel):
    """Detailed status response."""
    indexed: bool
    documents_count: int
    chunks_count: int
    vector_store_ready: bool
    errors: List[str]



rag_workflow = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes the RAG workflow and loads existing index on startup.
    """
    global rag_workflow
    
    logger.info(" Starting RAG API server...")
    
    try:
        from workflow import create_rag_workflow
        
        llm_service = os.getenv("LLM_SERVICE_TYPE", "ollama")
        
        rag_workflow = create_rag_workflow(
            enable_checkpointing=False,
            llm_service_type=llm_service,
        )
        
        if rag_workflow.load_existing_index():
            status = rag_workflow.get_status()
            logger.info(
                f" Loaded existing index: {status['chunks_count']} chunks from "
                f"{status['documents_count']} documents"
            )
        else:
            logger.warning(" No existing index found. Please index documents first.")
        
        logger.info(" RAG API ready to serve requests")
        
    except Exception as e:
        logger.error(f" Failed to initialize RAG workflow: {e}")
        raise
    
    yield
    
    logger.info(" Shutting down RAG API server...")



app = FastAPI(
    title="StarTech RAG API",
    description="API de Retrieval-Augmented Generation pour les risques majeurs",
    version="1.0.0",
    lifespan=lifespan,
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://.*:.*",  # Allow all localhost origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)



@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "StarTech RAG API",
        "version": "1.0.0",
        "description": "API pour le système RAG des risques majeurs",
        "endpoints": {
            "ask": "/ask - Poser une question",
            "search": "/search - Rechercher dans les documents",
            "health": "/health - État de santé de l'API",
            "status": "/status - Statut détaillé du système",
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns the current status of the RAG system.
    """
    if rag_workflow is None:
        return HealthResponse(
            status="unhealthy",
            indexed=False,
            documents_count=0,
            chunks_count=0,
        )
    
    status = rag_workflow.get_status()
    
    return HealthResponse(
        status="healthy" if status["indexed"] else "ready",
        indexed=status["indexed"],
        documents_count=status["documents_count"],
        chunks_count=status["chunks_count"],
    )


@app.get("/status", response_model=StatusResponse, tags=["Health"])
async def get_status():
    """
    Get detailed system status.
    """
    if rag_workflow is None:
        raise HTTPException(status_code=503, detail="RAG workflow not initialized")
    
    status = rag_workflow.get_status()
    
    return StatusResponse(
        indexed=status["indexed"],
        documents_count=status["documents_count"],
        chunks_count=status["chunks_count"],
        vector_store_ready=status["vector_store_ready"],
        errors=status["errors"],
    )


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the RAG system.
    
    The question is processed through the RAG pipeline:
    1. Semantic search in the vector store
    2. BM25 keyword search
    3. Hybrid result fusion
    4. LLM synthesis with citations
    
    Returns a comprehensive answer with sources.
    """
    if rag_workflow is None:
        raise HTTPException(status_code=503, detail="RAG workflow not initialized")
    
    if not rag_workflow.get_status()["indexed"]:
        raise HTTPException(
            status_code=400,
            detail="Aucun document indexé. Veuillez d'abord indexer des documents."
        )
    
    logger.info(f" Question received: {request.question[:100]}...")
    
    try:
        import time
        start_time = time.time()
        
        result = rag_workflow.query(request.question)
        
        processing_time = time.time() - start_time
        
        citations = []
        sources = set()
        
        for citation in result.citations:
            sources.add(citation.get("source", "Unknown"))
            citations.append(Citation(
                content=citation.get("content", ""),
                source=citation.get("source", "Unknown"),
                page=citation.get("page"),
                relevance_score=citation.get("score"),
            ))
        
        logger.info(f" Response generated in {processing_time:.2f}s")
        
        return AskResponse(
            answer=result.answer,
            sources=list(sources),
            citations=citations,
            confidence=result.confidence,
            processing_time=processing_time,
        )
        
    except Exception as e:
        logger.error(f" Error processing question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la question: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse, tags=["RAG"])
async def search_documents(request: SearchRequest):
    """
    Search for relevant documents/chunks.
    
    Performs hybrid search (semantic + BM25) without LLM synthesis.
    Useful for exploring the document base.
    """
    if rag_workflow is None:
        raise HTTPException(status_code=503, detail="RAG workflow not initialized")
    
    if not rag_workflow.get_status()["indexed"]:
        raise HTTPException(
            status_code=400,
            detail="Aucun document indexé."
        )
    
    logger.info(f" Search query: {request.query[:100]}...")
    
    try:
        context_agent = rag_workflow._current_state.get("_context_agent")
        
        if context_agent is None:
            raise HTTPException(
                status_code=503,
                detail="Context agent not available"
            )
        
        search_results = context_agent.search(request.query, top_k=request.top_k)
        
        results = []
        for chunk, score in search_results:
            results.append(SearchResult(
                content=chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
                source=chunk.source_file,
                score=score,
                page=chunk.page_number,
            ))
        
        return SearchResponse(
            results=results,
            total=len(results),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error during search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )


@app.post("/index", tags=["Admin"])
async def index_documents(pdf_paths: List[str]):
    """
    Index PDF documents.
    
    Admin endpoint to add new documents to the RAG system.
    """
    if rag_workflow is None:
        raise HTTPException(status_code=503, detail="RAG workflow not initialized")
    
    logger.info(f" Indexing {len(pdf_paths)} documents...")
    
    try:
        result = rag_workflow.index_documents(pdf_paths)
        
        return {
            "status": result["status"],
            "documents_processed": result["documents_processed"],
            "chunks_created": result["chunks_created"],
            "errors": result["errors"],
        }
        
    except Exception as e:
        logger.error(f" Error during indexing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'indexation: {str(e)}"
        )


@app.post("/reset", tags=["Admin"])
async def reset_workflow():
    """
    Reset the RAG workflow state.
    
    Admin endpoint to clear the current state.
    """
    if rag_workflow is None:
        raise HTTPException(status_code=503, detail="RAG workflow not initialized")
    
    rag_workflow.reset()
    
    return {"status": "reset", "message": "Workflow state cleared"}



if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    logger.info(f" Starting server on {host}:{port}")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
