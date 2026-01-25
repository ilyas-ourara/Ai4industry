"""
Main entry point for the RAG Multi-Agent Application.
Provides CLI interface for running the RAG pipeline.
"""

import sys
from pathlib import Path
from typing import List, Optional
import argparse

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<dim>{message}</dim>",
    level="WARNING",  # Only show warnings and errors in console
    filter=lambda record: "Main" not in record["extra"].get("component", "")
)
logger.add(
    "logs/rag_app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)

logger = logger.bind(component="Main", name="Main")


def index_documents(pdf_paths: List[str], output_dir: Optional[str] = None):
    """
    Index PDF documents.
    
    Args:
        pdf_paths: List of paths to PDF files
        output_dir: Optional output directory for markdown files
    """
    from workflow import create_rag_workflow
    
    logger.info(f"Indexing {len(pdf_paths)} documents...")
    
    workflow = create_rag_workflow()
    result = workflow.index_documents(pdf_paths)
    
    print("\n" + "="*50)
    print(" INDEXATION TERMINÉE")
    print("="*50)
    print(f" Documents traités: {result['documents_processed']}")
    print(f" Chunks créés: {result['chunks_created']}")
    
    if result['errors']:
        print(f"  Erreurs: {len(result['errors'])}")
        for err in result['errors']:
            print(f"   - {err}")
    
    return workflow


def query_documents(workflow, question: str):
    """
    Query indexed documents.
    
    Args:
        workflow: RAGWorkflow instance with indexed documents
        question: User's question
    """
    logger.info(f"Processing query: {question[:50]}...")
    
    print("\n Recherche en cours...\n")
    
    result = workflow.query(question)
    
    print(f"\n Réponse:\n")
    print(f"{result.answer}\n")
    
    if result.citations:
        sources = set(c['source'] for c in result.citations)
        print(f" Sources: {', '.join(sources)}")
    
    print()
    
    return result


def run_full_pipeline(pdf_paths: List[str], question: str):
    """
    Run the complete RAG pipeline.
    
    Args:
        pdf_paths: List of paths to PDF files
        question: User's question
    """
    from workflow import create_rag_workflow
    
    logger.info("Running full RAG pipeline...")
    
    workflow = create_rag_workflow(llm_service_type="mock")
    result = workflow.run_full_pipeline(pdf_paths, question)
    
    print("\n" + "="*50)
    print(" PIPELINE RAG COMPLET")
    print("="*50)
    
    print(f"\n Indexation:")
    print(f"   - Documents: {result['indexing']['documents_processed']}")
    print(f"   - Chunks: {result['indexing']['chunks_created']}")
    
    if result['synthesis']:
        synthesis = result['synthesis']
        print(f"\n Question: {synthesis.query}")
        print(f"\n Réponse:\n{synthesis.answer}")
        print(f"\n Confiance: {synthesis.confidence:.0%}")
    
    if result['errors']:
        print(f"\n  Erreurs:")
        for err in result['errors']:
            print(f"   - {err}")
    
    return result


def interactive_mode(workflow=None, llm_service_type: str = "ollama"):
    """
    Run interactive query mode.
    
    Args:
        workflow: Optional pre-configured workflow
        llm_service_type: Type of LLM service to use
    """
    from workflow import create_rag_workflow
    
    if workflow is None:
        workflow = create_rag_workflow(llm_service_type=llm_service_type)
        
        if workflow.load_existing_index():
            print("\n Données existantes chargées depuis ChromaDB!")
    
    print("\n" + "="*50)
    print(" MODE INTERACTIF")
    print("="*50)
    print("Tapez vos questions (ou 'quit' pour quitter)")
    print("Commandes: /index <chemin>, /status, /reset, /help\n")
    
    if workflow._indexed:
        status = workflow.get_status()
        print(f" {status['chunks_count']} chunks prêts pour la recherche\n")
    
    while True:
        try:
            user_input = input(" Votre question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Au revoir! ")
                break
            
            if user_input.startswith('/'):
                handle_command(user_input, workflow)
                continue
            
            if not workflow._indexed:
                print("  Aucun document indexé. Utilisez /index <chemin> d'abord.")
                continue
            
            query_documents(workflow, user_input)
            
        except KeyboardInterrupt:
            print("\nAu revoir! ")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f" Erreur: {e}")


def handle_command(command: str, workflow):
    """Handle CLI commands."""
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    if cmd == '/index':
        if not args:
            print("Usage: /index <chemin_pdf>")
            return
        pdf_paths = [p.strip() for p in args.split(',')]
        workflow.index_documents(pdf_paths)
        
    elif cmd == '/status':
        status = workflow.get_status()
        print(f"\n Statut:")
        print(f"   - Indexé: {'Oui' if status['indexed'] else 'Non'}")
        print(f"   - Documents: {status['documents_count']}")
        print(f"   - Chunks: {status['chunks_count']}")
        print(f"   - Vector Store: {'Prêt' if status['vector_store_ready'] else 'Non prêt'}")
        
    elif cmd == '/reset':
        workflow.reset()
        print(" État réinitialisé")
        
    elif cmd == '/help':
        print("\n Commandes disponibles:")
        print("   /index <chemin>  - Indexer un document PDF")
        print("   /status          - Afficher le statut")
        print("   /reset           - Réinitialiser")
        print("   /help            - Afficher l'aide")
        print("   quit             - Quitter")
    else:
        print(f" Commande inconnue: {cmd}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Multi-Agent Application pour documents DDRM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py --index data/DDRM_vienne_86.pdf
  python main.py --query "Quels sont les risques d'inondation?"
  python main.py --index data/*.pdf --query "Risques naturels?"
  python main.py --interactive
        """
    )
    
    parser.add_argument(
        '--index', '-i',
        nargs='+',
        help='Chemins vers les fichiers PDF à indexer'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Question à poser sur les documents'
    )
    
    parser.add_argument(
        '--interactive', '-I',
        action='store_true',
        help='Lancer le mode interactif'
    )
    
    parser.add_argument(
        '--llm',
        type=str,
        default='ollama',
        choices=['openai', 'ollama', 'mock'],
        help='Service LLM à utiliser (default: ollama)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    print("\n" + "="*50)
    print(" RAG MULTI-AGENT APPLICATION")
    print("   Documents DDRM - Risques Majeurs")
    print("="*50)
    
    try:
        if args.interactive:
            workflow = None
            if args.index:
                from workflow import create_rag_workflow
                workflow = create_rag_workflow(llm_service_type=args.llm)
                workflow.index_documents(args.index)
            interactive_mode(workflow, llm_service_type=args.llm)
            
        elif args.index and args.query:
            run_full_pipeline(args.index, args.query)
            
        elif args.index:
            index_documents(args.index)
            
        elif args.query:
            print("  Veuillez d'abord indexer des documents avec --index")
            sys.exit(1)
            
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
