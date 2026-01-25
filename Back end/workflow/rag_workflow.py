"""
RAG Workflow - Main orchestration class using LangGraph.
Provides high-level interface for the multi-agent RAG system.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from core.models import AgentState, SynthesisResult, ExtractedDocument
from .graph_builder import (
    build_full_rag_graph,
    build_query_only_graph,
    build_indexing_graph,
)


class RAGWorkflow:
    """
    Main RAG Workflow orchestrator.
    
    Provides a high-level interface to:
    - Index documents (PDF extraction + embedding)
    - Query indexed documents
    - Run full pipeline (index + query)
    
    Uses LangGraph for workflow orchestration.
    """

    def __init__(
        self,
        enable_checkpointing: bool = False,
        llm_service_type: str = "mock",
    ):
        """
        Initialize the RAG workflow.
        
        Args:
            enable_checkpointing: Enable state checkpointing for recovery
            llm_service_type: Type of LLM service to use
        """
        self._logger = logger.bind(component="RAGWorkflow")
        self.enable_checkpointing = enable_checkpointing
        self.llm_service_type = llm_service_type
        
        self._full_graph = None
        self._query_graph = None
        self._indexing_graph = None
        
        self._current_state: AgentState = {}
        self._indexed = False

    @property
    def full_graph(self):
        """Lazy-load full RAG graph."""
        if self._full_graph is None:
            self._logger.info("Building full RAG graph...")
            self._full_graph = build_full_rag_graph(self.enable_checkpointing)
        return self._full_graph

    @property
    def query_graph(self):
        """Lazy-load query-only graph."""
        if self._query_graph is None:
            self._logger.info("Building query graph...")
            self._query_graph = build_query_only_graph(self.enable_checkpointing)
        return self._query_graph

    @property
    def indexing_graph(self):
        """Lazy-load indexing graph."""
        if self._indexing_graph is None:
            self._logger.info("Building indexing graph...")
            self._indexing_graph = build_indexing_graph(self.enable_checkpointing)
        return self._indexing_graph

    def index_documents(
        self,
        pdf_paths: Union[str, Path, List[Union[str, Path]]],
    ) -> Dict[str, Any]:
        """
        Index PDF documents for later querying.
        
        Args:
            pdf_paths: Path(s) to PDF files
            
        Returns:
            Dict with indexing results and statistics
        """
        self._logger.info("Starting document indexing...")
        
        if isinstance(pdf_paths, (str, Path)):
            pdf_paths = [str(pdf_paths)]
        else:
            pdf_paths = [str(p) for p in pdf_paths]
        
        initial_state: AgentState = {
            "pdf_paths": pdf_paths,
            "errors": [],
            "processing_status": {},
        }
        
        final_state = self.indexing_graph.invoke(initial_state)
        
        self._current_state = final_state
        self._indexed = True
        
        result = {
            "status": "success" if not final_state.get("errors") else "partial",
            "documents_processed": len(final_state.get("extracted_documents", [])),
            "chunks_created": len(final_state.get("chunks", [])),
            "errors": final_state.get("errors", []),
            "processing_status": final_state.get("processing_status", {}),
        }
        
        self._logger.info(
            f"Indexing complete: {result['documents_processed']} documents, "
            f"{result['chunks_created']} chunks"
        )
        
        return result

    def query(
        self,
        question: str,
        use_existing_index: bool = True,
    ) -> SynthesisResult:
        """
        Query the indexed documents.
        
        Args:
            question: User's question
            use_existing_index: Use existing indexed chunks
            
        Returns:
            SynthesisResult with answer and citations
        """
        self._logger.info(f"Processing query: {question[:50]}...")
        
        if use_existing_index and not self._indexed:
            raise ValueError(
                "No documents indexed. Call index_documents() first "
                "or set use_existing_index=False"
            )
        
        query_state: AgentState = {
            "query": question,
            "chunks": self._current_state.get("chunks", []),
            "vector_store_ready": self._current_state.get("vector_store_ready", False),
            "_context_agent": self._current_state.get("_context_agent"),
            "llm_service_type": self.llm_service_type,
            "errors": [],
            "processing_status": {},
        }
        
        final_state = self.query_graph.invoke(query_state)
        
        synthesis = final_state.get("synthesis")
        
        if not synthesis:
            from core.models import SynthesisResult
            synthesis = SynthesisResult(
                query=question,
                answer="Désolé, je n'ai pas pu générer de réponse.",
                citations=[],
                sources=[],
                confidence=0.0,
                processing_time=0.0,
            )
        
        return synthesis

    def run_full_pipeline(
        self,
        pdf_paths: Union[str, Path, List[Union[str, Path]]],
        question: str,
    ) -> Dict[str, Any]:
        """
        Run the complete RAG pipeline: index + query.
        
        Args:
            pdf_paths: Path(s) to PDF files
            question: User's question
            
        Returns:
            Dict with full pipeline results
        """
        self._logger.info("Running full RAG pipeline...")
        
        if isinstance(pdf_paths, (str, Path)):
            pdf_paths = [str(pdf_paths)]
        else:
            pdf_paths = [str(p) for p in pdf_paths]
        
        initial_state: AgentState = {
            "pdf_paths": pdf_paths,
            "query": question,
            "errors": [],
            "processing_status": {},
        }
        
        final_state = self.full_graph.invoke(initial_state)
        
        self._current_state = final_state
        self._indexed = True
        
        synthesis = final_state.get("synthesis")
        
        result = {
            "status": "success" if synthesis else "partial",
            "indexing": {
                "documents_processed": len(final_state.get("extracted_documents", [])),
                "chunks_created": len(final_state.get("chunks", [])),
            },
            "synthesis": synthesis,
            "errors": final_state.get("errors", []),
            "processing_status": final_state.get("processing_status", {}),
        }
        
        self._logger.info("Full pipeline complete")
        
        return result

    def get_indexed_documents(self) -> List[ExtractedDocument]:
        """Get list of indexed documents."""
        return self._current_state.get("extracted_documents", [])

    def get_chunks(self) -> List:
        """Get all indexed chunks."""
        return self._current_state.get("chunks", [])

    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "indexed": self._indexed,
            "documents_count": len(self._current_state.get("extracted_documents", [])),
            "chunks_count": len(self._current_state.get("chunks", [])),
            "vector_store_ready": self._current_state.get("vector_store_ready", False),
            "processing_status": self._current_state.get("processing_status", {}),
            "errors": self._current_state.get("errors", []),
        }

    def reset(self):
        """Reset the workflow state."""
        self._current_state = {}
        self._indexed = False
        self._logger.info("Workflow state reset")

    def load_existing_index(self) -> bool:
        """
        Load existing indexed data from ChromaDB.
        Allows using previously indexed documents without re-indexing.
        
        Returns:
            True if existing data was loaded, False otherwise
        """
        self._logger.info("Checking for existing indexed data...")
        
        try:
            from agents.agent_2_context import ContextConstructionAgent
            
            context_agent = ContextConstructionAgent()
            
            # Check if there's data in the vector store
            chunk_count = context_agent.vector_store.count()
            
            if chunk_count > 0:
                chunks = context_agent.vector_store.get_all_chunks()
                
                self._current_state = {
                    "chunks": chunks,
                    "vector_store_ready": True,
                    "_context_agent": context_agent,
                    "errors": [],
                    "processing_status": {"loaded_from_existing": True},
                }
                self._indexed = True
                
                self._logger.info(f"Loaded {chunk_count} existing chunks from ChromaDB")
                return True
            else:
                self._logger.info("No existing indexed data found")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to load existing index: {e}")
            return False


def create_rag_workflow(
    enable_checkpointing: bool = False,
    llm_service_type: str = "mock",
) -> RAGWorkflow:
    """
    Factory function to create a RAG workflow instance.
    
    Args:
        enable_checkpointing: Enable state checkpointing
        llm_service_type: Type of LLM service
        
    Returns:
        Configured RAGWorkflow instance
    """
    return RAGWorkflow(
        enable_checkpointing=enable_checkpointing,
        llm_service_type=llm_service_type,
    )
