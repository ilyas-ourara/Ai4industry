import os
import json
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import ollama
import re

# -----------------------
# CONFIG
# -----------------------
DATA_FILE = "./data/ddrm_chunks.json"
OLLAMA_BASE_URL = "http://home.ngimenez.fr:11434"  # remote Ollama
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "mistral-3"
CHROMA_DB_DIR = "./chroma_db"

# -----------------------
# FASTAPI
# -----------------------
app = FastAPI(title="Auto-RAG API with JSON chunks")

# -----------------------
# CHROMA
# -----------------------
chroma_client = chromadb.Client(Settings(
    persist_directory=CHROMA_DB_DIR,
    anonymized_telemetry=False
))
collection = chroma_client.get_or_create_collection(name="ddrm_documents")

def split_text(text, max_chars=2000):
    # split du block
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current += "\n\n" + para if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i+max_chars])
                current = ""
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks

# envoie des chuncks vers ollama
def ollama_embed(text: str):
    response = ollama.embed(model=EMBED_MODEL, input=text)
    print("Ollama embed response:", response) # edbug
    # au cas ou
    if "embeddings" in response:
        return response.embeddings[0]
    elif hasattr(response, "embeddings"):
        return response.embeddings
    else:
        raise ValueError(f"No 'embeddings' in Ollama response: {response}")


def ollama_generate(prompt: str, max_tokens=300, temperature=0.2):
    # generation avec llm
    result = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"temperature": temperature, "num_predict": max_tokens}
    )
    return result["response"]

# Chargement des chuncks du json
def ingest_json_chunks():
    if not os.path.exists(DATA_FILE):
        print(f"⚠️ JSON file not found: {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = data.get("chunks", [])
    print(f"Found {len(chunks)} chunks in JSON.")

    for i, chunk in enumerate(chunks):
        content = chunk.get("content", "").strip()
        if not content:
            continue

        # Split car superieur > 300
        sub_chunks = split_text(content, max_chars=2000)

        for sub in sub_chunks:
            try:
                emb = ollama_embed(sub)
            except Exception as e:
                print(f"⚠️ Skipping sub-chunk due to embedding error: {e}")
                continue

            collection.add(
                ids=[str(uuid.uuid4())],
                embeddings=[emb],
                documents=[sub],
                metadatas=[{
                    "source_file": chunk.get("source_file"),
                    "section": chunk.get("section"),
                    "chunk_type": chunk.get("chunk_type"),
                    "position_in_document": chunk.get("position_in_document")
                }]
            )

@app.on_event("startup")
def startup_event():
    ingest_json_chunks()

class EmbeddingRequest(BaseModel):
    input: str

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 300
    temperature: float = 0.2

@app.post("/v1/embeddings")
def embeddings(req: EmbeddingRequest):
    try:
        emb = ollama_embed(req.input)
        return {"data": [{"embedding": emb}]}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/v1/completions")
def completions(req: CompletionRequest):
    try:
        query_emb = ollama_embed(req.prompt)

        docs = collection.query(
            query_embeddings=[query_emb],
            n_results=3
        )["documents"][0]

        context = "\n\n".join(docs)
        rag_prompt = f"""
You are a helpful assistant. Use the context to answer the question.

CONTEXT:
{context}

QUESTION:
{req.prompt}
"""

        answer = ollama_generate(rag_prompt, req.max_tokens, req.temperature)
        return {"choices": [{"text": answer}]}

    except Exception as e:
        raise HTTPException(500, str(e))
