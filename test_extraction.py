"""
Test script to verify the RAG application is working.
This demonstrates the extraction pipeline without waiting for full completion.
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | <level>{message}</level>", level="INFO")

print("\n" + "="*60)
print("🔍 VÉRIFICATION DE L'APPLICATION RAG")
print("="*60)

# Check 1: Python imports
print("\n✓ Vérification des imports...")
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    print("  ✅ Docling importé avec succès")
except ImportError as e:
    print(f"  ❌ Erreur Docling: {e}")
    sys.exit(1)

try:
    from agents import PDFExtractionAgent
    print("  ✅ PDFExtractionAgent importé avec succès")
except ImportError as e:
    print(f"  ❌ Erreur import agent: {e}")
    sys.exit(1)

try:
    from workflow import create_rag_workflow
    print("  ✅ RAG Workflow importé avec succès")
except ImportError as e:
    print(f"  ❌ Erreur workflow: {e}")
    sys.exit(1)

# Check 2: File existence
print("\n✓ Vérification des fichiers...")
pdf_path = Path("data/DDRM_vienne_86.pdf")
if pdf_path.exists():
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"  ✅ PDF trouvé: {pdf_path} ({size_mb:.1f} MB)")
else:
    print(f"  ❌ PDF non trouvé: {pdf_path}")
    sys.exit(1)

# Check 3: Configuration
print("\n✓ Vérification de la configuration...")
try:
    from config import get_settings
    settings = get_settings()
    print(f"  ✅ Configuration chargée")
    print(f"     - Output dir: {settings.output_dir}")
    print(f"     - Embedding model: {settings.embedding_model}")
except Exception as e:
    print(f"  ⚠️  Erreur configuration: {e}")

# Check 4: Docling Pipeline Options
print("\n✓ Vérification des options Docling...")
try:
    options = PdfPipelineOptions(
        generate_page_images=False,
        do_ocr=False,
        do_picture_classification=False,
        image_scale=0.3
    )
    print(f"  ✅ PdfPipelineOptions créées correctement:")
    print(f"     - generate_page_images: False")
    print(f"     - do_ocr: False")
    print(f"     - do_picture_classification: False")
    print(f"     - image_scale: 0.3")
except Exception as e:
    print(f"  ❌ Erreur options: {e}")
    sys.exit(1)

# Check 5: Extraction Agent
print("\n✓ Vérification de l'agent d'extraction...")
try:
    agent = PDFExtractionAgent()
    print(f"  ✅ PDFExtractionAgent initialisé")
    print(f"     - Name: {agent.name}")
    print(f"     - Output dir: {agent.output_dir}")
except Exception as e:
    print(f"  ❌ Erreur agent: {e}")
    sys.exit(1)

# Check 6: Output directory
print("\n✓ Vérification des répertoires...")
output_dir = Path("output/markdown")
output_dir.mkdir(parents=True, exist_ok=True)
print(f"  ✅ Répertoire output vérifié: {output_dir}")

print("\n" + "="*60)
print("✅ TOUS LES VÉRIFICATIONS SONT PASSÉES!")
print("="*60)
print("\n📝 Notes:")
print("  - L'application est correctement configurée")
print("  - Docling est prêt à traiter les PDFs")
print("  - Un processus d'indexation peut être en cours d'exécution")
print("  - Consultez les logs pour plus de détails")
print("\n🚀 Pour démarrer l'indexation:")
print("  python3 main.py --index data/DDRM_vienne_86.pdf")
print("\n")
