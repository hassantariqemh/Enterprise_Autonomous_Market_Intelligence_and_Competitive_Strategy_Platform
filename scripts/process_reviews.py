"""
Processes unprocessed raw_reviews rows: matches product names, computes
a text-based sentiment score, links them to Neo4j Product nodes, and
marks rows as processed.
Run with: python scripts/process_reviews.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from textblob import TextBlob
from app.utils.postgres_connection import db as pg_db
from app.utils.neo4j_connection import db as neo4j_db

KNOWN_PRODUCTS = [
    "Galaxy S25", "Galaxy A55", "iPhone 16", "iPhone 16e",
    "Xiaomi 15", "Redmi Note 14", "OnePlus 13", "Pixel 9",
]


def match_product(product_name):
    for p in KNOWN_PRODUCTS:
        if p.lower() == product_name.strip().lower():
            return p
    return None


def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity  # -1.0 to +1.0
    return round(polarity, 3)


def process_reviews():
    rows = pg_db.run_query(
        "SELECT id, product_name, review_text, rating FROM raw_reviews WHERE processed = FALSE",
        fetch=True,
    )

    if not rows:
        print("No unprocessed reviews found.")
        return

    for review_id, product_name, review_text, rating in rows:
        matched_product = match_product(product_name)
        sentiment = get_sentiment(review_text)

        if matched_product:
            neo4j_db.run_query(
                """
                MERGE (r:Review {id: $review_id})
                SET r.text = $review_text, r.rating = $rating, r.sentiment = $sentiment
                WITH r
                MATCH (p:Product {name: $product_name})
                MERGE (r)-[:REVIEWS]->(p)
                """,
                {
                    "review_id": f"review_{review_id}",
                    "review_text": review_text,
                    "rating": rating,
                    "sentiment": sentiment,
                    "product_name": matched_product,
                },
            )

        pg_db.run_query(
            "UPDATE raw_reviews SET processed = TRUE WHERE id = %(id)s",
            {"id": review_id},
        )

        print(f"Review {review_id}: product={matched_product or 'no match'}, sentiment={sentiment} -> marked processed.")

    print(f"\n{len(rows)} reviews processed.")


if __name__ == "__main__":
    process_reviews()
    pg_db.close()
    neo4j_db.close()
    print("Review processing complete.")