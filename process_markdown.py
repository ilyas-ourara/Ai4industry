#!/usr/bin/env python3
"""
Script to process existing Markdown files directly with Agent 2.
Bypasses Agent 1 (PDF extraction) and goes straight to chunking + embedding.
"""

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

from agents.agent_2_context import ContextConstructionAgent
from agents.agent_2_context.markdown_parser import MarkdownParser
from core.models import ExtractionResult

def process_markdown_file(markdown_path: str):
    """
    Process a Markdown file with Agent 2.
    
    Args:
        markdown_path: Path to the Markdown file
    """
    logger.info(f"Processing Markdown: {markdown_path}")
    
    markdown_file = Path(markdown_path)
    if not markdown_file.exists():
        logger.error(f"File not found: {markdown_path}")
        sys.exit(1)
    
    try:
        # Initialize agents
        parser = MarkdownParser()
        context_agent = ContextConstructionAgent()
        
        # Read markdown
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info("Parsing Markdown...")
        parsed = parser.parse(content)
        
        logger.info(f"Found: {len(parsed.sections)} sections, {len(parsed.links)} links, {len(parsed.tables)} tables")
        
        # Process with Agent 2
        logger.info("Processing with Context Construction Agent...")
        
        # Create ExtractionResult object (what Agent 2 expects)
        extraction_result = ExtractionResult(
            source_file=markdown_file.name,
            markdown_content=content,
            output_path=str(markdown_file),
            success=True,
            processing_time=0.0
        )
        
        result = context_agent.process_markdown_content([extraction_result])
        
        print("\n" + "="*60)
        print("✅ TRAITEMENT TERMINÉ")
        print("="*60)
        print(f"📄 Fichier: {markdown_file.name}")
        print(f"📦 Chunks créés: {len(result.get('chunks', []))}")
        print(f"✨ Embeddings générés: {result.get('embeddings_stored', False)}")
        print(f"🔍 Vector Store prêt: {result.get('vector_store_ready', False)}")
        
        # Afficher le chemin du JSON exporté
        json_path = result.get('stats', {}).get('json_export_path')
        if json_path:
            print(f"📋 Chunks JSON: {json_path}")
        
        print("="*60)
        print("\n🎯 Vous pouvez maintenant lancer des requêtes!\n")
        
        return result
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_markdown.py <markdown_file>")
        print("\nExemple:")
        print("  python3 process_markdown.py output/markdown/DDRM_vienne_86.md")
        sys.exit(1)
    
    markdown_path = sys.argv[1]
    process_markdown_file(markdown_path)
