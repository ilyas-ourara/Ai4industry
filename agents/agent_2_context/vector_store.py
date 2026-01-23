"""
Vector Store Manager for Agent 2.
Manages ChromaDB and FAISS vector stores for document storage and retrieval.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from config import get_settings
from core.models import DocumentChunk, SearchResult


class VectorStoreManager:
    """
    Manages vector storage using ChromaDB (primary) with FAISS fallback.
    Handles document storage, indexing, and similarity search.
    """

    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[Path] = None,
        use_faiss: bool = False,
    ):
        """
        Initialize the vector store manager.
        
        Args:
            collection_name: Name for the ChromaDB collection
            persist_directory: Directory for persistent storage
            use_faiss: Use FAISS instead of ChromaDB
        """
        self.settings = get_settings()
        self.collection_name = collection_name or self.settings.chroma_collection_name
        self.persist_directory = persist_directory or self.settings.get_absolute_path(
            self.settings.chroma_persist_directory
        )
        self.use_faiss = use_faiss
        
        self._logger = logger.bind(component="VectorStoreManager")
        
        # Initialize stores
        self._chroma_client = None
        self._collection = None
        self._faiss_index = None
        self._document_store: Dict[str, DocumentChunk] = {}
        
        self._initialize_store()

    def _initialize_store(self):
        """Initialize the vector store."""
        if self.use_faiss:
            self._initialize_faiss()
        else:
            self._initialize_chroma()

    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            
            self._logger.info(f"Initializing ChromaDB at: {self.persist_directory}")
            
            # Create persist directory
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize client with persistence (new API)
            self._chroma_client = chromadb.PersistentClient(
                path=str(self.persist_directory)
            )
            
            # Get or create collection
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "DDRM document chunks"}
            )
            
            self._logger.info(
                f"ChromaDB collection '{self.collection_name}' initialized "
                f"with {self._collection.count()} existing documents"
            )
            
        except ImportError:
            self._logger.warning("ChromaDB not installed, falling back to FAISS")
            self.use_faiss = True
            self._initialize_faiss()
        except Exception as e:
            self._logger.error(f"ChromaDB initialization failed: {e}")
            raise

    def _initialize_faiss(self):
        """Initialize FAISS index."""
        try:
            import faiss
            
            self._logger.info("Initializing FAISS index")
            
            # Create index (will be properly sized on first add)
            dimension = self.settings.embedding_dimension
            self._faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine sim
            
            # Load existing index if available
            index_path = self.persist_directory / "faiss_index.bin"
            docs_path = self.persist_directory / "documents.json"
            
            if index_path.exists() and docs_path.exists():
                self._faiss_index = faiss.read_index(str(index_path))
                with open(docs_path, "r") as f:
                    stored_docs = json.load(f)
                    self._document_store = {
                        k: DocumentChunk(**v) for k, v in stored_docs.items()
                    }
                self._logger.info(f"Loaded existing FAISS index with {len(self._document_store)} documents")
            
        except ImportError:
            self._logger.error("FAISS not installed")
            raise ImportError("Please install faiss-cpu: pip install faiss-cpu")

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> int:
        """
        Add document chunks with their embeddings to the store.
        
        Args:
            chunks: List of DocumentChunk objects
            embeddings: Corresponding embeddings for each chunk
            
        Returns:
            Number of chunks added
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")
        
        if not chunks:
            return 0
        
        self._logger.info(f"Adding {len(chunks)} chunks to vector store")
        
        if self.use_faiss:
            return self._add_to_faiss(chunks, embeddings)
        else:
            return self._add_to_chroma(chunks, embeddings)

    def _add_to_chroma(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> int:
        """Add chunks to ChromaDB."""
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [self._chunk_to_metadata(chunk) for chunk in chunks]
        
        # ChromaDB has a batch limit
        batch_size = 100
        added = 0
        
        for i in range(0, len(chunks), batch_size):
            batch_end = min(i + batch_size, len(chunks))
            
            self._collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end],
            )
            added += batch_end - i
        
        # Persistent client automatically persists changes
        
        self._logger.info(f"Added {added} chunks to ChromaDB")
        return added

    def _add_to_faiss(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> int:
        """Add chunks to FAISS index."""
        import numpy as np
        import faiss
        
        # Normalize embeddings for cosine similarity
        embed_array = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embed_array)
        
        # Add to index
        self._faiss_index.add(embed_array)
        
        # Store documents
        for chunk in chunks:
            self._document_store[chunk.id] = chunk
        
        # Persist
        self._save_faiss()
        
        self._logger.info(f"Added {len(chunks)} chunks to FAISS")
        return len(chunks)

    def _save_faiss(self):
        """Save FAISS index and document store to disk."""
        import faiss
        
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        index_path = self.persist_directory / "faiss_index.bin"
        docs_path = self.persist_directory / "documents.json"
        
        faiss.write_index(self._faiss_index, str(index_path))
        
        with open(docs_path, "w") as f:
            json.dump(
                {k: v.model_dump() for k, v in self._document_store.items()},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def _chunk_to_metadata(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """Convert chunk to metadata dict for storage."""
        return {
            "source_file": chunk.source_file,
            "chapter": chunk.chapter or "",
            "chapter_number": chunk.chapter_number or 0,
            "section": chunk.section or "",
            "section_number": chunk.section_number or 0,
            "subsection": chunk.subsection or "",
            "page_number": chunk.page_number or 0,
            "chunk_type": chunk.chunk_type,
            "position": chunk.position_in_document,
        }

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        if self.use_faiss:
            return self._search_faiss(query_embedding, top_k)
        else:
            return self._search_chroma(query_embedding, top_k, filter_metadata)

    def _search_chroma(
        self,
        query_embedding: List[float],
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search ChromaDB collection."""
        where_filter = None
        if filter_metadata:
            where_filter = {k: v for k, v in filter_metadata.items() if v}
        
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
        
        search_results = []
        
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                content = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 0
                
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                score = 1 / (1 + distance)
                
                chunk = DocumentChunk(
                    id=doc_id,
                    content=content,
                    source_file=metadata.get("source_file", ""),
                    chapter=metadata.get("chapter") or None,
                    chapter_number=metadata.get("chapter_number") or None,
                    section=metadata.get("section") or None,
                    section_number=metadata.get("section_number") or None,
                    subsection=metadata.get("subsection") or None,
                    page_number=metadata.get("page_number") or None,
                    chunk_type=metadata.get("chunk_type", "paragraph"),
                    position_in_document=metadata.get("position", 0),
                )
                
                search_results.append(SearchResult(
                    chunk=chunk,
                    score=score,
                    vector_score=score,
                    rank=i + 1,
                ))
        
        return search_results

    def _search_faiss(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[SearchResult]:
        """Search FAISS index."""
        import numpy as np
        import faiss
        
        # Normalize query
        query_array = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_array)
        
        # Search
        scores, indices = self._faiss_index.search(query_array, top_k)
        
        search_results = []
        doc_ids = list(self._document_store.keys())
        
        for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx < 0 or idx >= len(doc_ids):
                continue
            
            doc_id = doc_ids[idx]
            chunk = self._document_store[doc_id]
            
            search_results.append(SearchResult(
                chunk=chunk,
                score=float(score),
                vector_score=float(score),
                rank=i + 1,
            ))
        
        return search_results

    def get_all_chunks(self) -> List[DocumentChunk]:
        """Get all stored chunks."""
        if self.use_faiss:
            return list(self._document_store.values())
        else:
            # Get from ChromaDB
            results = self._collection.get(include=["documents", "metadatas"])
            chunks = []
            
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                content = results["documents"][i] if results["documents"] else ""
                
                chunk = DocumentChunk(
                    id=doc_id,
                    content=content,
                    source_file=metadata.get("source_file", ""),
                    chapter=metadata.get("chapter") or None,
                    section=metadata.get("section") or None,
                    page_number=metadata.get("page_number") or None,
                    chunk_type=metadata.get("chunk_type", "paragraph"),
                )
                chunks.append(chunk)
            
            return chunks

    def delete_collection(self):
        """Delete the entire collection."""
        if self.use_faiss:
            import faiss
            dimension = self.settings.embedding_dimension
            self._faiss_index = faiss.IndexFlatIP(dimension)
            self._document_store.clear()
            
            # Remove files
            index_path = self.persist_directory / "faiss_index.bin"
            docs_path = self.persist_directory / "documents.json"
            if index_path.exists():
                index_path.unlink()
            if docs_path.exists():
                docs_path.unlink()
        else:
            self._chroma_client.delete_collection(self.collection_name)
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name
            )
        
        self._logger.info("Collection deleted")

    def count(self) -> int:
        """Get the number of documents in the store."""
        if self.use_faiss:
            return len(self._document_store)
        else:
            return self._collection.count()
