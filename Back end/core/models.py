"""
Pydantic models for data structures used across the multi-agent system.
Ensures type safety and validation throughout the pipeline.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class DocumentType(str, Enum):
    """Type of document being processed."""
    DDRM = "ddrm"
    API = "api"
    GENERIC = "generic"


class ChunkType(str, Enum):
    """Type of content chunk."""
    TITLE = "title"
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    FIGURE = "figure"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    
    source_file: str = Field(..., description="Nom du fichier source")
    document_type: DocumentType = Field(default=DocumentType.GENERIC)
    title: Optional[str] = Field(default=None, description="Titre du document")
    department: Optional[str] = Field(default=None, description="Département concerné")
    creation_date: Optional[datetime] = Field(default=None)
    extraction_date: datetime = Field(default_factory=datetime.now)
    total_pages: int = Field(default=0, description="Nombre total de pages")
    language: str = Field(default="fr", description="Langue du document")
    """Metadata for a document."""
    
    class Config:
        use_enum_values = True


class DocumentChunk(BaseModel):
    """
    Represents a semantic chunk of a document.
    Preserves hierarchy and context information.
    """
    
    id: str = Field(..., description="Identifiant unique du chunk")
    content: str = Field(..., description="Contenu textuel du chunk")
    chunk_type: ChunkType = Field(default=ChunkType.PARAGRAPH)
    
    chapter: Optional[str] = Field(default=None, description="Chapitre parent")
    chapter_number: Optional[int] = Field(default=None)
    section: Optional[str] = Field(default=None, description="Section parente")
    section_number: Optional[int] = Field(default=None)
    subsection: Optional[str] = Field(default=None, description="Sous-section parente")
    
    page_number: Optional[int] = Field(default=None, description="Numéro de page")
    start_page: Optional[int] = Field(default=None)
    end_page: Optional[int] = Field(default=None)
    position_in_document: int = Field(default=0, description="Position ordinale")
    
    source_file: str = Field(..., description="Fichier source")
    
    embedding: Optional[List[float]] = Field(default=None, exclude=True)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

    def get_hierarchy_path(self) -> str:
        """Get the hierarchical path of this chunk."""
        parts = []
        if self.chapter:
            parts.append(f"Chapitre {self.chapter_number}: {self.chapter}")
        if self.section:
            parts.append(f"Section {self.section_number}: {self.section}")
        if self.subsection:
            parts.append(self.subsection)
        return " > ".join(parts) if parts else "Document Root"

    def to_context_string(self) -> str:
        """Convert chunk to a context string for LLM."""
        context = f"[Source: {self.source_file}"
        if self.page_number:
            context += f", Page {self.page_number}"
        context += f"]\n"
        context += f"[{self.get_hierarchy_path()}]\n"
        context += f"{self.content}"
        return context


class ExtractedDocument(BaseModel):
    """
    Represents a fully extracted document with all its chunks.
    Output of Agent 1 (PDF Extraction).
    """
    
    metadata: DocumentMetadata
    markdown_content: str = Field(..., description="Contenu Markdown complet")
    chunks: List[DocumentChunk] = Field(default_factory=list)
    table_of_contents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Table des matières extraite"
    )
    
    def get_chunks_by_chapter(self, chapter: str) -> List[DocumentChunk]:
        """Get all chunks belonging to a specific chapter."""
        return [c for c in self.chunks if c.chapter == chapter]
    
    def get_chunks_by_page(self, page: int) -> List[DocumentChunk]:
        """Get all chunks from a specific page."""
        return [c for c in self.chunks if c.page_number == page]


class ExtractionResult(BaseModel):
    """
    Result of PDF extraction with Docling.
    Simple model for Agent 1 output (PDF → Markdown brut).
    """
    
    source_file: str = Field(..., description="Nom du fichier PDF source")
    markdown_content: str = Field(..., description="Contenu Markdown brut extrait")
    output_path: str = Field(..., description="Chemin du fichier Markdown généré")
    success: bool = Field(default=True, description="Extraction réussie")
    error_message: Optional[str] = Field(default=None, description="Message d'erreur si échec")
    processing_time: float = Field(default=0.0, description="Temps d'extraction en secondes")


class SearchResult(BaseModel):
    """
    Represents a search result from the retrieval system.
    Used by Agent 3 (Research & Synthesis).
    """
    
    chunk: DocumentChunk
    score: float = Field(..., description="Score de pertinence")
    bm25_score: Optional[float] = Field(default=None)
    vector_score: Optional[float] = Field(default=None)
    rank: int = Field(default=0, description="Rang dans les résultats")
    
    class Config:
        arbitrary_types_allowed = True


class SynthesisResult(BaseModel):
    """
    Represents the final synthesis output.
    Produced by Agent 3.
    """
    
    query: str = Field(..., description="Question originale")
    answer: str = Field(..., description="Réponse synthétisée")
    citations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Citations avec sources"
    )
    sources: List[SearchResult] = Field(
        default_factory=list,
        description="Sources utilisées"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score de confiance"
    )
    processing_time: float = Field(default=0.0, description="Temps de traitement en secondes")


class AgentState(TypedDict, total=False):
    """
    State shared between agents in the LangGraph workflow.
    """
    pdf_paths: List[str]
    query: Optional[str]
    
    extraction_results: List[ExtractionResult]
    extracted_documents: List[ExtractedDocument]
    markdown_files: List[str]
    
    chunks: List[DocumentChunk]
    embeddings_stored: bool
    vector_store_ready: bool
    
    search_results: List[SearchResult]
    synthesis: Optional[SynthesisResult]
    
    current_agent: str
    errors: List[str]
    processing_status: Dict[str, str]
