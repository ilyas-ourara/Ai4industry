"""
Embedding Service for Agent 2.
Calculates embeddings for document chunks using sentence-transformers.
"""

from typing import List, Optional, Union
import numpy as np
from loguru import logger

from config import get_settings


class EmbeddingService:
    """
    Service for calculating text embeddings.
    Uses sentence-transformers for local embedding generation.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformer model to use.
                       Defaults to settings.embedding_model
        """
        self.settings = get_settings()
        self.model_name = model_name or self.settings.embedding_model
        self._model = None
        self._logger = logger.bind(component="EmbeddingService")
        
        self._logger.info(f"Initializing EmbeddingService with model: {self.model_name}")

    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            self._load_model()
        return self._model

    def _load_model(self):
        """Load the sentence-transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            self._logger.info(f"Loading model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._logger.info("Model loaded successfully")
            
        except ImportError:
            self._logger.error("sentence-transformers not installed")
            raise ImportError(
                "Please install sentence-transformers: pip install sentence-transformers"
            )
        except Exception as e:
            self._logger.error(f"Failed to load model: {e}")
            raise

    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        if not text or not text.strip():
            self._logger.warning("Empty text provided for embedding")
            return [0.0] * self.embedding_dimension
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not texts:
            return []
        
        self._logger.info(f"Embedding {len(texts)} texts...")
        
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            return [[0.0] * self.embedding_dimension for _ in texts]
        
        embeddings = self.model.encode(
            valid_texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )
        
        result = [[0.0] * self.embedding_dimension for _ in texts]
        for idx, embedding in zip(valid_indices, embeddings):
            result[idx] = embedding.tolist()
        
        self._logger.info(f"Generated {len(valid_texts)} embeddings")
        return result

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        Some models have specific query encoding.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding
        """
        return self.embed_text(query)

    def compute_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))

    def find_most_similar(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        top_k: int = 5,
    ) -> List[tuple]:
        """
        Find the most similar embeddings to a query.
        
        Args:
            query_embedding: Query embedding
            embeddings: List of embeddings to search
            top_k: Number of results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if not embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        embed_matrix = np.array(embeddings)
        
        dot_products = np.dot(embed_matrix, query_vec)
        norms = np.linalg.norm(embed_matrix, axis=1) * np.linalg.norm(query_vec)
        
        norms = np.where(norms == 0, 1, norms)
        similarities = dot_products / norms
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]

    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize an embedding to unit length.
        
        Args:
            embedding: Embedding to normalize
            
        Returns:
            Normalized embedding
        """
        vec = np.array(embedding)
        norm = np.linalg.norm(vec)
        
        if norm == 0:
            return embedding
        
        return (vec / norm).tolist()
