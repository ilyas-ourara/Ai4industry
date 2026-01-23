# RAG Multi-Agent Application

Application RAG (Retrieval-Augmented Generation) multi-agents basée sur LangGraph pour l'analyse des Documents Départementaux sur les Risques Majeurs (DDRM).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DDRM.pdf (Vienne/Deux-Sèvres)               │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ analyse
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Agent 1: Extraction PDF                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐        │
│  │ PyMuPDF/OCR  │→ │ Structure Detect │→ │ Markdown Gen    │        │
│  └──────────────┘  └──────────────────┘  └─────────────────┘        │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ génère
                          ▼
                   ┌──────────────────┐
                   │ Markdown Structuré│
                   └────────┬─────────┘
                            │ traite
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Agent 2: Construction Contexte                       │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐        │
│  │ Parser MD    │→ │ Calc Embeddings  │→ │ Store ChromaDB  │        │
│  └──────────────┘  └──────────────────┘  └─────────────────┘        │
└────────┬────────────────────┬───────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌────────────────┐    ┌───────────────────┐
│ JSON + Metadata│    │ Vector DB (Chroma)│
└────────┬───────┘    └─────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Agent 3: Recherche & Synthèse                        │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐        │
│  │ Hybrid Search│→ │ Select Passages  │→ │ LLM Synthesis   │        │
│  │ (BM25+Vector)│  │                  │  │ (Otoroshi)      │        │
│  └──────────────┘  └──────────────────┘  └─────────────────┘        │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ produit
                          ▼
                ┌─────────────────────┐
                │ Résumé + Citations  │
                └─────────────────────┘
```

## 📁 Structure du Projet

```
project/
├── agents/                          # Agents spécialisés
│   ├── agent_1_extraction/          # Agent d'extraction PDF
│   │   ├── __init__.py
│   │   ├── pdf_extraction_agent.py  # Agent principal
│   │   ├── extractors.py            # PyMuPDF, OCR, etc.
│   │   ├── structure_detector.py    # Détection structure DDRM
│   │   └── markdown_generator.py    # Génération Markdown
│   │
│   ├── agent_2_context/             # Agent de construction contexte
│   │   ├── __init__.py
│   │   ├── context_construction_agent.py
│   │   ├── markdown_parser.py       # Parser Markdown
│   │   ├── embedding_service.py     # Service embeddings
│   │   └── vector_store.py          # ChromaDB/FAISS
│   │
│   └── agent_3_synthesis/           # Agent de recherche & synthèse
│       ├── __init__.py
│       ├── research_synthesis_agent.py
│       ├── hybrid_search.py         # BM25 + Vector search
│       ├── llm_service.py           # Otoroshi/OpenAI
│       └── prompts.py               # Templates de prompts
│
├── core/                            # Composants partagés
│   ├── __init__.py
│   ├── base_agent.py                # Classe de base des agents
│   └── models.py                    # Modèles Pydantic
│
├── config/                          # Configuration
│   ├── __init__.py
│   └── settings.py                  # Settings Pydantic
│
├── workflow/                        # Orchestration LangGraph
│   ├── __init__.py
│   ├── graph_builder.py             # Construction du graphe
│   ├── nodes.py                     # Nœuds du workflow
│   └── rag_workflow.py              # Workflow principal
│
├── data/                            # Données
│   ├── DDRM_vienne_86.pdf
│   └── DDRM_deux_sevres.pdf
│
├── output/                          # Sorties générées
│   └── markdown/
│
├── main.py                          # Point d'entrée CLI
├── requirements.txt                 # Dépendances
├── .env.example                     # Variables d'environnement
└── README.md
```

## 🚀 Installation

### Prérequis

- Python 3.10+
- pip ou conda

### Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos paramètres
nano .env
```

Variables importantes:
- `OTOROSHI_API_URL`: URL du service LLM Otoroshi
- `OTOROSHI_API_KEY`: Clé API Otoroshi
- `EMBEDDING_MODEL`: Modèle d'embeddings (default: sentence-transformers/all-MiniLM-L6-v2)

## 📖 Utilisation

### Mode CLI

```bash
# Indexer des documents
python main.py --index data/DDRM_vienne_86.pdf

# Poser une question (après indexation)
python main.py --index data/DDRM_vienne_86.pdf --query "Quels sont les risques d'inondation?"

# Mode interactif
python main.py --interactive

# Avec service LLM spécifique
python main.py --index data/*.pdf --query "Risques naturels?" --llm otoroshi
```

### Mode Programmatique

```python
from workflow import create_rag_workflow

# Créer le workflow
workflow = create_rag_workflow(llm_service_type="otoroshi")

# Indexer des documents
result = workflow.index_documents([
    "data/DDRM_vienne_86.pdf",
    "data/DDRM_deux_sevres.pdf"
])

# Poser des questions
response = workflow.query("Quels sont les risques d'inondation dans la Vienne?")

print(response.answer)
print(response.citations)
```

### Utilisation des agents individuellement

```python
from agents import PDFExtractionAgent, ContextConstructionAgent, ResearchSynthesisAgent

# Agent 1: Extraction
extractor = PDFExtractionAgent()
documents = extractor.process("data/DDRM_vienne_86.pdf")

# Agent 2: Indexation
context_agent = ContextConstructionAgent()
context_agent.process(documents)

# Agent 3: Recherche
synthesis_agent = ResearchSynthesisAgent(
    context_agent=context_agent,
    llm_service_type="otoroshi"
)
synthesis_agent.prepare()

result = synthesis_agent.ask("Quels sont les risques majeurs?")
```

## 🔧 Configuration Avancée

### Paramètres de chunking

```python
# Dans config/settings.py ou .env
CHUNK_SIZE=1000        # Taille des chunks en caractères
CHUNK_OVERLAP=200      # Chevauchement entre chunks
```

### Recherche hybride

```python
# Poids BM25 vs Vector search
BM25_WEIGHT=0.3
VECTOR_WEIGHT=0.7
TOP_K_RESULTS=5
```

### Modèles d'embeddings

Modèles supportés:
- `sentence-transformers/all-MiniLM-L6-v2` (default, léger)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingue)
- `sentence-transformers/all-mpnet-base-v2` (plus précis)

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=agents --cov=core tests/
```

## 📊 Fonctionnalités

### Agent 1: Extraction PDF
- ✅ Extraction texte avec PyMuPDF
- ✅ Fallback OCR pour documents scannés
- ✅ Détection structure DDRM (chapitres, sections)
- ✅ Génération Markdown structuré
- ✅ Extraction tables et métadonnées

### Agent 2: Construction Contexte
- ✅ Parsing Markdown avec frontmatter
- ✅ Embeddings avec sentence-transformers
- ✅ Stockage ChromaDB avec persistance
- ✅ Export JSON avec métadonnées

### Agent 3: Recherche & Synthèse
- ✅ Recherche hybride BM25 + vectorielle
- ✅ Reciprocal Rank Fusion (RRF)
- ✅ Synthèse LLM via Otoroshi
- ✅ Citations avec sources
- ✅ Score de confiance

### Orchestration LangGraph
- ✅ Workflow complet (index + query)
- ✅ Workflow indexation seule
- ✅ Workflow requête seule
- ✅ Checkpointing optionnel
- ✅ Gestion des erreurs

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -am 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- Développé dans le cadre du Master 2 IA
