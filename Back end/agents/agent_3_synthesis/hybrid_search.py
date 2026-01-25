"""
Hybrid Search Engine for Agent 3.
Combines BM25 keyword search with vector similarity search.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from loguru import logger
from rank_bm25 import BM25Okapi

from config import get_settings
from core.models import DocumentChunk, SearchResult


class HybridSearchEngine:
    """
    Hybrid search combining BM25 (lexical) and vector (semantic) search.
    Uses Reciprocal Rank Fusion (RRF) for result combination.
    """

    def __init__(
        self,
        bm25_weight: Optional[float] = None,
        vector_weight: Optional[float] = None,
        rrf_k: int = 60,
    ):
        """
        Initialize the hybrid search engine.
        
        Args:
            bm25_weight: Weight for BM25 scores (0-1)
            vector_weight: Weight for vector scores (0-1)
            rrf_k: RRF constant (default 60)
        """
        self.settings = get_settings()
        self.bm25_weight = bm25_weight or self.settings.bm25_weight
        self.vector_weight = vector_weight or self.settings.vector_weight
        self.rrf_k = rrf_k
        
        self._logger = logger.bind(component="HybridSearchEngine")
        
        self._bm25: Optional[BM25Okapi] = None
        self._corpus: List[str] = []
        self._chunks: List[DocumentChunk] = []
        
        self._logger.info(
            f"Initialized HybridSearchEngine "
            f"(BM25 weight: {self.bm25_weight}, Vector weight: {self.vector_weight})"
        )

    def index_chunks(self, chunks: List[DocumentChunk]):
        """
        Index chunks for BM25 search.
        
        Args:
            chunks: List of DocumentChunk to index
        """
        self._logger.info(f"Indexing {len(chunks)} chunks for BM25")
        
        self._chunks = chunks
        self._corpus = []
        
        tokenized_corpus = []
        
        for chunk in chunks:
            text = self._create_searchable_text(chunk)
            self._corpus.append(text)
            
            tokens = self._tokenize(text)
            tokenized_corpus.append(tokens)
        
        self._bm25 = BM25Okapi(tokenized_corpus)
        
        self._logger.info(f"BM25 index built with {len(tokenized_corpus)} documents")

    def _create_searchable_text(self, chunk: DocumentChunk) -> str:
        """Create searchable text from chunk with context."""
        parts = []
        
        if chunk.chapter:
            parts.append(f"chapitre {chunk.chapter}")
        if chunk.section:
            parts.append(f"section {chunk.section}")
        if chunk.subsection:
            parts.append(chunk.subsection)
        
        parts.append(chunk.content)
        
        return " ".join(parts).lower()

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25.
        Simple whitespace tokenization with basic normalization.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        import re
        
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        
        tokens = [t.strip() for t in text.split() if t.strip()]
        
        stopwords = {
            "le", "la", "les", "de", "du", "des", "un", "une",
            "et", "en", "à", "au", "aux", "pour", "par", "sur",
            "dans", "ce", "ces", "cette", "est", "sont", "été",
            "a", "ont", "qui", "que", "dont", "ou", "il", "elle",
            "nous", "vous", "ils", "elles", "se", "son", "sa", "ses",
        }
        
        tokens = [t for t in tokens if len(t) > 2 and t not in stopwords]
        
        return tokens

    def bm25_search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Tuple[int, float]]:
        """
        Perform BM25 search.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (chunk_index, score) tuples
        """
        if self._bm25 is None:
            self._logger.warning("BM25 index not built")
            return []
        
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        scores = self._bm25.get_scores(query_tokens)
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]

    def hybrid_search(
        self,
        query: str,
        vector_results: List[SearchResult],
        top_k: int = 5,
        use_rrf: bool = True,
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining BM25 and vector results.
        
        Args:
            query: Search query
            vector_results: Results from vector search
            top_k: Number of results to return
            use_rrf: Use Reciprocal Rank Fusion (vs weighted combination)
            
        Returns:
            List of combined SearchResult
        """
        self._logger.info(f"Performing hybrid search for: {query[:50]}...")
        
        bm25_results = self.bm25_search(query, top_k=top_k * 2)
        
        bm25_scores: Dict[str, float] = {}
        bm25_ranks: Dict[str, int] = {}
        
        for rank, (idx, score) in enumerate(bm25_results):
            if idx < len(self._chunks):
                chunk_id = self._chunks[idx].id
                bm25_scores[chunk_id] = score
                bm25_ranks[chunk_id] = rank + 1
        
        vector_scores: Dict[str, float] = {}
        vector_ranks: Dict[str, int] = {}
        
        for result in vector_results:
            vector_scores[result.chunk.id] = result.score
            vector_ranks[result.chunk.id] = result.rank
        
        if use_rrf:
            combined = self._reciprocal_rank_fusion(
                bm25_ranks, vector_ranks, top_k
            )
        else:
            combined = self._weighted_combination(
                bm25_scores, vector_scores, top_k
            )
        
        final_results = []
        chunk_map = {c.id: c for c in self._chunks}
        
        for rank, (chunk_id, combined_score) in enumerate(combined):
            chunk = chunk_map.get(chunk_id)
            
            if not chunk:
                for vr in vector_results:
                    if vr.chunk.id == chunk_id:
                        chunk = vr.chunk
                        break
            
            if chunk:
                final_results.append(SearchResult(
                    chunk=chunk,
                    score=combined_score,
                    bm25_score=bm25_scores.get(chunk_id, 0),
                    vector_score=vector_scores.get(chunk_id, 0),
                    rank=rank + 1,
                ))
        
        self._logger.info(f"Hybrid search returned {len(final_results)} results")
        return final_results

    def _reciprocal_rank_fusion(
        self,
        bm25_ranks: Dict[str, int],
        vector_ranks: Dict[str, int],
        top_k: int,
    ) -> List[Tuple[str, float]]:
        """
        Combine rankings using Reciprocal Rank Fusion.
        
        RRF score = sum(1 / (k + rank)) for each result list
        
        Args:
            bm25_ranks: Chunk ID to BM25 rank mapping
            vector_ranks: Chunk ID to vector rank mapping
            top_k: Number of results
            
        Returns:
            List of (chunk_id, rrf_score) sorted by score
        """
        rrf_scores: Dict[str, float] = {}
        
        all_ids = set(bm25_ranks.keys()) | set(vector_ranks.keys())
        
        for chunk_id in all_ids:
            score = 0.0
            
            if chunk_id in bm25_ranks:
                score += self.bm25_weight / (self.rrf_k + bm25_ranks[chunk_id])
            
            if chunk_id in vector_ranks:
                score += self.vector_weight / (self.rrf_k + vector_ranks[chunk_id])
            
            rrf_scores[chunk_id] = score
        
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def _weighted_combination(
        self,
        bm25_scores: Dict[str, float],
        vector_scores: Dict[str, float],
        top_k: int,
    ) -> List[Tuple[str, float]]:
        """
        Combine scores using weighted average.
        
        Args:
            bm25_scores: Chunk ID to normalized BM25 score
            vector_scores: Chunk ID to vector score
            top_k: Number of results
            
        Returns:
            List of (chunk_id, combined_score) sorted by score
        """
        combined_scores: Dict[str, float] = {}
        
        if bm25_scores:
            max_bm25 = max(bm25_scores.values())
            if max_bm25 > 0:
                bm25_scores = {k: v / max_bm25 for k, v in bm25_scores.items()}
        
        all_ids = set(bm25_scores.keys()) | set(vector_scores.keys())
        
        for chunk_id in all_ids:
            bm25_score = bm25_scores.get(chunk_id, 0)
            vector_score = vector_scores.get(chunk_id, 0)
            
            combined = (
                self.bm25_weight * bm25_score +
                self.vector_weight * vector_score
            )
            combined_scores[chunk_id] = combined
        
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a chunk by its ID."""
        for chunk in self._chunks:
            if chunk.id == chunk_id:
                return chunk
        return None

    @property
    def is_indexed(self) -> bool:
        """Check if chunks are indexed."""
        return self._bm25 is not None and len(self._chunks) > 0
