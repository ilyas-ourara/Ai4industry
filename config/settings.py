"""
Configuration settings for the RAG Multi-Agent Application.
Uses Pydantic for validation and environment variable loading.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project Paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent
    )
    data_dir: Path = Field(default=Path("data"))
    output_dir: Path = Field(default=Path("output"))

    # LLM Configuration - Otoroshi
    otoroshi_api_url: str = Field(
        default="https://your-otoroshi-service.com/api",
        description="URL du service LLM Otoroshi"
    )
    otoroshi_api_key: str = Field(
        default="",
        description="Clé API Otoroshi"
    )

    # Ollama Configuration
    ollama_api_url: str = Field(
        default="http://localhost:11434",
        description="URL de l'API Ollama"
    )
    ollama_model: str = Field(
        default="llama3.2:1b",
        description="Modèle Ollama à utiliser"
    )

    # OpenAI Fallback
    openai_api_key: Optional[str] = Field(
        default=None,
        description="Clé API OpenAI (fallback)"
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Modèle d'embeddings"
    )
    embedding_dimension: int = Field(
        default=384,
        description="Dimension des vecteurs d'embeddings"
    )

    # ChromaDB Configuration
    chroma_persist_directory: Path = Field(
        default=Path("data/chroma_db"),
        description="Répertoire de persistance ChromaDB"
    )
    chroma_collection_name: str = Field(
        default="ddrm_documents",
        description="Nom de la collection ChromaDB"
    )

    # Chunking Configuration
    chunk_size: int = Field(
        default=1000,
        description="Taille des chunks en caractères"
    )
    chunk_overlap: int = Field(
        default=200,
        description="Chevauchement entre chunks"
    )

    # LLM Configuration
    max_tokens: int = Field(
        default=4096,
        description="Nombre maximum de tokens pour le LLM"
    )
    temperature: float = Field(
        default=0.1,
        description="Température pour la génération LLM"
    )

    # Search Configuration
    top_k_results: int = Field(
        default=5,
        description="Nombre de résultats à retourner"
    )
    bm25_weight: float = Field(
        default=0.3,
        description="Poids de BM25 dans la recherche hybride"
    )
    vector_weight: float = Field(
        default=0.7,
        description="Poids de la recherche vectorielle"
    )

    # Logging
    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_absolute_path(self, relative_path: Path) -> Path:
        """Convert relative path to absolute based on project root."""
        if relative_path.is_absolute():
            return relative_path
        return self.project_root / relative_path


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
