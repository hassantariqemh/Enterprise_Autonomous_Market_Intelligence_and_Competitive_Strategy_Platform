"""
Quick test: runs a semantic search query against the ChromaDB RAG index.
Run with: python scripts/test_rag_search.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "chroma_data")

client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_or_create_collection(
    name="market_intel_docs",
    embedding_function=embedding_fn,
)

query = "Which competitor changed pricing recently?"
results = collection.query(query_texts=[query], n_results=3)

for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    print(f"\n--- Result {i+1} ---")
    print(f"Type: {meta.get('type')}")
    print(f"Metadata: {meta}")
    print(f"Text: {doc[:150]}...")