"""
Processes unprocessed raw_articles rows: extracts company mentions using
spaCy NER, links them to Neo4j Company nodes, and marks rows as processed.
Run with: python scripts/process_articles.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

import spacy
from app.utils.postgres_connection import db as pg_db
from app.utils.neo4j_connection import db as neo4j_db

nlp = spacy.load("en_core_web_sm")

# Known companies in our knowledge graph (used to validate/normalize spaCy's ORG guesses)
KNOWN_COMPANIES = ["Samsung", "Apple", "Xiaomi", "OnePlus", "Google"]


def extract_companies(text):
    doc = nlp(text)
    found = set()
    for ent in doc.ents:
        if ent.label_ == "ORG":
            for company in KNOWN_COMPANIES:
                if company.lower() in ent.text.lower():
                    found.add(company)
    return found


def process_articles():
    rows = pg_db.run_query(
        "SELECT id, title, content FROM raw_articles WHERE processed = FALSE",
        fetch=True,
    )

    if not rows:
        print("No unprocessed articles found.")
        return

    for article_id, title, content in rows:
        text = f"{title}. {content}"
        companies = extract_companies(text)

        for company in companies:
            neo4j_db.run_query(
                """
                MERGE (a:Article {id: $article_id})
                SET a.title = $title
                WITH a
                MATCH (c:Company {name: $company})
                MERGE (a)-[:MENTIONS]->(c)
                """,
                {"article_id": f"article_{article_id}", "title": title, "company": company},
            )

        pg_db.run_query(
            "UPDATE raw_articles SET processed = TRUE WHERE id = %(id)s",
            {"id": article_id},
        )

        print(f"Article {article_id}: found companies {companies or 'none'} -> marked processed.")

    print(f"\n{len(rows)} articles processed.")


if __name__ == "__main__":
    process_articles()
    pg_db.close()
    neo4j_db.close()
    print("Article processing complete.")