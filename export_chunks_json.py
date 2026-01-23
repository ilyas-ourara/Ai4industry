#!/usr/bin/env python3
"""
Script to export existing chunks from ChromaDB to JSON file.
"""

import json
import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
    level="INFO",
)

def export_chunks_to_json(output_path: str = "output/chunks/chunks.json"):
    """
    Export all chunks from ChromaDB to JSON file.
    
    Args:
        output_path: Path for the output JSON file
    """
    from config import get_settings
    
    settings = get_settings()
    
    # Initialize ChromaDB directly
    try:
        import chromadb
        
        persist_dir = settings.get_absolute_path(settings.chroma_persist_directory)
        logger.info(f"Connecting to ChromaDB at: {persist_dir}")
        
        client = chromadb.PersistentClient(path=str(persist_dir))
        collection = client.get_or_create_collection(name=settings.chroma_collection_name)
        
        count = collection.count()
        logger.info(f"Found {count} chunks in ChromaDB")
        
        if count == 0:
            logger.warning("No chunks found in ChromaDB")
            return
        
        # Get all documents with metadata
        results = collection.get(include=["documents", "metadatas"])
        
        # Build chunks list
        chunks = []
        for i, doc_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i] if results["metadatas"] else {}
            content = results["documents"][i] if results["documents"] else ""
            
            chunk = {
                "id": doc_id,
                "content": content,
                "source_file": metadata.get("source_file", ""),
                "chapter": metadata.get("chapter") or None,
                "chapter_number": metadata.get("chapter_number") or None,
                "section": metadata.get("section") or None,
                "section_number": metadata.get("section_number") or None,
                "subsection": metadata.get("subsection") or None,
                "page_number": metadata.get("page_number") or None,
                "chunk_type": metadata.get("chunk_type", "paragraph"),
                "position_in_document": metadata.get("position", 0),
            }
            chunks.append(chunk)
        
        # Sort by position
        chunks.sort(key=lambda x: x.get("position_in_document", 0))
        
        # Build output data
        data = {
            "metadata": {
                "total_chunks": len(chunks),
                "collection_name": settings.chroma_collection_name,
                "export_date": str(__import__("datetime").datetime.now()),
            },
            "chunks": chunks,
        }
        
        # Save to JSON
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Exported {len(chunks)} chunks to {output_file}")
        
        print("\n" + "="*60)
        print("✅ EXPORT JSON TERMINÉ")
        print("="*60)
        print(f"📦 Chunks exportés: {len(chunks)}")
        print(f"📋 Fichier JSON: {output_file.absolute()}")
        print("="*60)
        
    except ImportError:
        logger.error("ChromaDB not installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "output/chunks/chunks.json"
    export_chunks_to_json(output_path)
