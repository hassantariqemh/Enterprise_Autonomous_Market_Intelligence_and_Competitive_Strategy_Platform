"""
Builds a ChromaDB vector index from processed raw_articles and raw_reviews,
to support semantic search / RAG for the AI Strategy Advisor and Executive Copilot.
Run with: python scripts/build_rag_index.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

import chromadb
from chromadb.utils import embedding_functions
from app.utils.postgres_connection import db as pg_db

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "chroma_data")

client = chromadb.PersistentClient(path=CHROMA_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="market_intel_docs",
    embedding_function=embedding_fn,
)


def index_articles():
    rows = pg_db.run_query(
        "SELECT id, title, content, company_mentioned, published_date FROM raw_articles WHERE processed = TRUE",
        fetch=True,
    )
    for article_id, title, content, company, date in rows:
        doc_text = f"{title}. {content}"
        collection.add(
            ids=[f"article_{article_id}"],
            documents=[doc_text],
            metadatas=[{
                "type": "article",
                "company": company or "",
                "date": str(date),
                "title": title,
            }],
        )
    print(f"{len(rows)} articles indexed.")


def index_reviews():
    rows = pg_db.run_query(
        "SELECT id, product_name, review_text, rating, review_date FROM raw_reviews WHERE processed = TRUE",
        fetch=True,
    )
    for review_id, product_name, review_text, rating, date in rows:
        collection.add(
            ids=[f"review_{review_id}"],
            documents=[review_text],
            metadatas=[{
                "type": "review",
                "product": product_name or "",
                "rating": rating,
                "date": str(date),
            }],
        )
    print(f"{len(rows)} reviews indexed.")


if __name__ == "__main__":
    index_articles()
    index_reviews()
    pg_db.close()
    print("RAG index build complete.")