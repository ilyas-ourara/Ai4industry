"""
Context Construction Agent (Agent 2)
Responsible for parsing Markdown, computing embeddings, and storing in vector database.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from core.base_agent import BaseAgent
from core.models import DocumentChunk, ExtractedDocument, ExtractionResult, SearchResult

from .markdown_parser import MarkdownParser, ParsedMarkdown
from .embedding_service import EmbeddingService
from .vector_store import VectorStoreManager


class ContextConstructionAgent(BaseAgent):
    """
    Agent 2: Context Construction
    
    Responsibilities:
    - Parse Markdown documents
    - Calculate embeddings for chunks
    - Store chunks and embeddings in vector database (ChromaDB/FAISS)
    - Generate JSON data with metadata
    - Prepare data for semantic search
    
    Outputs:
    - Vector database ready for similarity search
    - JSON documents with full metadata
    """

    def __init__(
        self,
        collection_name: Optional[str] = None,
        use_faiss: bool = False,
    ):
        """
        Initialize the Context Construction Agent.
        
        Args:
            collection_name: Name for the vector store collection
            use_faiss: Use FAISS instead of ChromaDB
        """
        super().__init__(
            name="ContextConstructionAgent",
            description="Parses Markdown, computes embeddings, and stores in vector DB"
        )
        
        # Initialize components
        self.markdown_parser = MarkdownParser()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreManager(
            collection_name=collection_name,
            use_faiss=use_faiss,
        )
        
        self._processed_documents: List[ExtractedDocument] = []

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data.
        
        Args:
            input_data: ExtractedDocument(s) or Markdown path(s)
            
        Returns:
            True if valid
        """
        if isinstance(input_data, ExtractedDocument):
            return True
        elif isinstance(input_data, list):
            for item in input_data:
                if not isinstance(item, (ExtractedDocument, str, Path)):
                    raise ValueError(f"Invalid input type: {type(item)}")
            return True
        elif isinstance(input_data, (str, Path)):
            path = Path(input_data)
            if not path.exists():
                raise ValueError(f"File not found: {path}")
            return True
        else:
            raise ValueError(f"Invalid input type: {type(input_data)}")

    def process(
        self,
        input_data: Union[ExtractedDocument, List[ExtractedDocument], str, Path, List[str]],
    ) -> Dict[str, Any]:
        """
        Process documents and store in vector database.
        
        Args:
            input_data: ExtractedDocument(s) from Agent 1, or Markdown path(s)
            
        Returns:
            Dict with processing results and statistics
        """
        self.logger.info("Starting context construction process")
        
        # Validate input
        self.validate_input(input_data)
        
        # Normalize input
        documents = self._normalize_input(input_data)
        
        # Process each document
        all_chunks = []
        stats = {
            "documents_processed": 0,
            "total_chunks": 0,
            "embeddings_computed": 0,
            "chunks_stored": 0,
        }
        
        for doc in documents:
            chunks = self._process_document(doc)
            all_chunks.extend(chunks)
            stats["documents_processed"] += 1
            stats["total_chunks"] += len(chunks)
        
        # Compute embeddings
        self.logger.info(f"Computing embeddings for {len(all_chunks)} chunks...")
        embeddings = self._compute_embeddings(all_chunks)
        stats["embeddings_computed"] = len(embeddings)
        
        # Store in vector database
        self.logger.info("Storing chunks in vector database...")
        stored_count = self.vector_store.add_chunks(all_chunks, embeddings)
        stats["chunks_stored"] = stored_count
        
        # Update agent state
        self.update_state("chunks", all_chunks)
        self.update_state("embeddings_stored", True)
        self.update_state("vector_store_ready", True)
        
        self.logger.info(
            f"Context construction complete: "
            f"{stats['documents_processed']} docs, "
            f"{stats['chunks_stored']} chunks stored"
        )
        
        return {
            "status": "success",
            "stats": stats,
            "chunks": all_chunks,
        }

    def process_markdown_content(
        self,
        extraction_results: List[ExtractionResult],
    ) -> Dict[str, Any]:
        """
        Process raw Markdown content from Docling extraction results.
        
        This method handles the output of Agent 1 (Docling extraction)
        which produces raw Markdown strings.
        
        Args:
            extraction_results: List of ExtractionResult from Agent 1 (Docling)
            
        Returns:
            Dict with processing results and statistics
        """
        self.logger.info(f"Processing {len(extraction_results)} Docling extraction results")
        
        all_chunks = []
        stats = {
            "documents_processed": 0,
            "total_chunks": 0,
            "embeddings_computed": 0,
            "chunks_stored": 0,
            "failed_documents": 0,
        }
        
        for result in extraction_results:
            if not result.success:
                self.logger.warning(f"Skipping failed extraction: {result.source_file}")
                stats["failed_documents"] += 1
                continue
            
            try:
                # Parse raw Markdown from Docling
                parsed = self.markdown_parser.parse(result.markdown_content)
                
                # Create chunks from parsed content
                chunks = self._sections_to_chunks(parsed, result.source_file)
                
                all_chunks.extend(chunks)
                stats["documents_processed"] += 1
                stats["total_chunks"] += len(chunks)
                
                self.logger.info(
                    f"Processed {result.source_file}: {len(chunks)} chunks"
                )
                
            except Exception as e:
                self.logger.error(f"Error processing {result.source_file}: {e}")
                stats["failed_documents"] += 1
        
        # Compute embeddings
        if all_chunks:
            self.logger.info(f"Computing embeddings for {len(all_chunks)} chunks...")
            embeddings = self._compute_embeddings(all_chunks)
            stats["embeddings_computed"] = len(embeddings)
            
            # Store in vector database
            self.logger.info("Storing chunks in vector database...")
            stored_count = self.vector_store.add_chunks(all_chunks, embeddings)
            stats["chunks_stored"] = stored_count
        
        # Update agent state
        self.update_state("chunks", all_chunks)
        self.update_state("embeddings_stored", True)
        self.update_state("vector_store_ready", True)
        
        # Auto-export chunks to JSON
        if all_chunks:
            json_output_path = self.settings.get_absolute_path(
                self.settings.output_dir / "chunks" / "chunks.json"
            )
            self.export_to_json(json_output_path)
            stats["json_export_path"] = str(json_output_path)
        
        self.logger.info(
            f"Docling content processing complete: "
            f"{stats['documents_processed']} docs, "
            f"{stats['chunks_stored']} chunks stored"
        )
        
        return {
            "status": "success",
            "stats": stats,
            "chunks": all_chunks,
        }

    def process_markdown_files(
        self,
        markdown_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Process Markdown files from disk.
        
        Alternative entry point when working with saved Markdown files
        instead of in-memory extraction results.
        
        Args:
            markdown_paths: List of paths to Markdown files
            
        Returns:
            Dict with processing results and statistics
        """
        self.logger.info(f"Processing {len(markdown_paths)} Markdown files")
        
        all_chunks = []
        stats = {
            "documents_processed": 0,
            "total_chunks": 0,
            "embeddings_computed": 0,
            "chunks_stored": 0,
            "failed_files": 0,
        }
        
        for md_path in markdown_paths:
            path = Path(md_path)
            
            if not path.exists():
                self.logger.warning(f"File not found: {path}")
                stats["failed_files"] += 1
                continue
            
            try:
                # Parse Markdown file
                parsed = self.markdown_parser.parse_file(path)
                
                # Create chunks
                chunks = self._sections_to_chunks(parsed, path.name)
                
                all_chunks.extend(chunks)
                stats["documents_processed"] += 1
                stats["total_chunks"] += len(chunks)
                
                self.logger.info(f"Processed {path.name}: {len(chunks)} chunks")
                
            except Exception as e:
                self.logger.error(f"Error processing {path}: {e}")
                stats["failed_files"] += 1
        
        # Compute embeddings and store
        if all_chunks:
            self.logger.info(f"Computing embeddings for {len(all_chunks)} chunks...")
            embeddings = self._compute_embeddings(all_chunks)
            stats["embeddings_computed"] = len(embeddings)
            
            self.logger.info("Storing chunks in vector database...")
            stored_count = self.vector_store.add_chunks(all_chunks, embeddings)
            stats["chunks_stored"] = stored_count
        
        # Update state
        self.update_state("chunks", all_chunks)
        self.update_state("embeddings_stored", True)
        self.update_state("vector_store_ready", True)
        
        self.logger.info(
            f"Markdown files processing complete: "
            f"{stats['documents_processed']} files, "
            f"{stats['chunks_stored']} chunks stored"
        )
        
        return {
            "status": "success",
            "stats": stats,
            "chunks": all_chunks,
        }

    def _normalize_input(
        self,
        input_data: Union[ExtractedDocument, List[ExtractedDocument], str, Path, List[str]],
    ) -> List[ExtractedDocument]:
        """Normalize input to list of ExtractedDocument."""
        if isinstance(input_data, ExtractedDocument):
            return [input_data]
        
        elif isinstance(input_data, list):
            result = []
            for item in input_data:
                if isinstance(item, ExtractedDocument):
                    result.append(item)
                elif isinstance(item, (str, Path)):
                    # Load from Markdown file
                    doc = self._load_markdown_as_document(Path(item))
                    result.append(doc)
            return result
        
        elif isinstance(input_data, (str, Path)):
            return [self._load_markdown_as_document(Path(input_data))]
        
        return []

    def _load_markdown_as_document(self, md_path: Path) -> ExtractedDocument:
        """Load a Markdown file and create an ExtractedDocument."""
        from core.models import DocumentMetadata, DocumentType
        
        parsed = self.markdown_parser.parse_file(md_path)
        
        # Create metadata from frontmatter
        metadata = DocumentMetadata(
            source_file=md_path.name,
            document_type=DocumentType(parsed.frontmatter.get("document_type", "generic")),
            title=parsed.frontmatter.get("title") or parsed.title,
            department=parsed.frontmatter.get("department"),
            total_pages=parsed.frontmatter.get("total_pages", 0),
        )
        
        # Create chunks from sections
        chunks = self._sections_to_chunks(parsed, md_path.name)
        
        return ExtractedDocument(
            metadata=metadata,
            markdown_content=parsed.raw_content,
            chunks=chunks,
            table_of_contents=[],
        )

    def _sections_to_chunks(
        self,
        parsed: ParsedMarkdown,
        source_file: str,
    ) -> List[DocumentChunk]:
        """Convert parsed sections to DocumentChunk objects."""
        from core.models import ChunkType
        import hashlib
        
        chunks = []
        flat_sections = self.markdown_parser.flatten_sections(parsed.sections)
        
        for i, section in enumerate(flat_sections):
            if not section.content.strip():
                continue
            
            # Determine chunk type based on level
            chunk_type_map = {
                1: ChunkType.CHAPTER,
                2: ChunkType.SECTION,
                3: ChunkType.SUBSECTION,
            }
            chunk_type = chunk_type_map.get(section.level, ChunkType.PARAGRAPH)
            
            # Generate ID
            content_hash = hashlib.md5(section.content[:100].encode()).hexdigest()[:8]
            chunk_id = f"{source_file}_{i}_{content_hash}"
            
            # Get page number from metadata if available
            page_num = section.metadata.get("page")
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=section.content,
                chunk_type=chunk_type,
                chapter=section.title if section.level == 1 else None,
                section=section.title if section.level == 2 else None,
                subsection=section.title if section.level >= 3 else None,
                page_number=page_num,
                position_in_document=i,
                source_file=source_file,
            )
            chunks.append(chunk)
        
        return chunks

    def _process_document(self, document: ExtractedDocument) -> List[DocumentChunk]:
        """
        Process a single ExtractedDocument.
        
        Args:
            document: ExtractedDocument from Agent 1
            
        Returns:
            List of processed chunks
        """
        self.logger.info(f"Processing document: {document.metadata.source_file}")
        
        chunks = document.chunks
        
        if not chunks:
            self.logger.warning("Document has no chunks, creating from markdown")
            parsed = self.markdown_parser.parse(document.markdown_content)
            chunks = self._sections_to_chunks(
                parsed, 
                document.metadata.source_file
            )
        
        # Enhance chunks with additional context
        enhanced_chunks = self._enhance_chunks(chunks, document)
        
        self._processed_documents.append(document)
        
        return enhanced_chunks

    def _enhance_chunks(
        self,
        chunks: List[DocumentChunk],
        document: ExtractedDocument,
    ) -> List[DocumentChunk]:
        """
        Enhance chunks with additional metadata and context.
        
        Args:
            chunks: Original chunks
            document: Source document
            
        Returns:
            Enhanced chunks
        """
        enhanced = []
        
        for chunk in chunks:
            # Add document-level metadata to chunk metadata
            chunk.metadata.update({
                "document_title": document.metadata.title,
                "department": document.metadata.department,
                "document_type": document.metadata.document_type,
            })
            
            enhanced.append(chunk)
        
        return enhanced

    def _compute_embeddings(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """
        Compute embeddings for chunks.
        Uses chunk content with context for better semantic representation.
        
        Args:
            chunks: List of chunks to embed
            
        Returns:
            List of embedding vectors
        """
        # Create text representations for embedding
        texts = []
        
        for chunk in chunks:
            # Include hierarchy context in embedding text
            context_parts = []
            
            if chunk.chapter:
                context_parts.append(f"Chapitre: {chunk.chapter}")
            if chunk.section:
                context_parts.append(f"Section: {chunk.section}")
            if chunk.subsection:
                context_parts.append(f"Sous-section: {chunk.subsection}")
            
            context = " | ".join(context_parts)
            
            if context:
                text = f"{context}\n\n{chunk.content}"
            else:
                text = chunk.content
            
            texts.append(text)
        
        # Compute embeddings
        embeddings = self.embedding_service.embed_texts(texts)
        
        return embeddings

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search the vector store for relevant chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        self.logger.info(f"Searching for: {query[:50]}...")
        
        # Compute query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )
        
        self.logger.info(f"Found {len(results)} results")
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the stored data."""
        return {
            "total_chunks": self.vector_store.count(),
            "documents_processed": len(self._processed_documents),
            "embedding_model": self.embedding_service.model_name,
            "embedding_dimension": self.embedding_service.embedding_dimension,
        }

    def export_to_json(self, output_path: Path) -> Path:
        """
        Export all chunks to JSON file.
        
        Args:
            output_path: Path for output JSON file
            
        Returns:
            Path to created file
        """
        import json
        
        chunks = self.vector_store.get_all_chunks()
        
        data = {
            "metadata": {
                "total_chunks": len(chunks),
                "embedding_model": self.embedding_service.model_name,
            },
            "chunks": [chunk.model_dump(exclude={"embedding"}) for chunk in chunks],
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Exported {len(chunks)} chunks to {output_path}")
        return output_path

    def clear(self):
        """Clear all stored data."""
        self.vector_store.delete_collection()
        self._processed_documents.clear()
        self.clear_state()
        self.logger.info("All data cleared")
