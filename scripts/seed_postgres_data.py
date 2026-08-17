"""
Inserts sample raw articles and reviews into PostgreSQL,
to verify the raw-data pipeline before hooking up real scraping/NLP.
Run with: python scripts/seed_postgres_data.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.postgres_connection import db

ARTICLES = [
    {
        "source": "TechCrunch",
        "url": "https://example.com/article1",
        "title": "Samsung expands Galaxy A-series in Southeast Asia",
        "content": "Samsung announced today an expansion of its Galaxy A-series retail presence across Southeast Asian markets, aiming to capture budget-conscious consumers...",
        "published_date": "2025-03-20",
        "company_mentioned": "Samsung",
    },
    {
        "source": "The Verge",
        "url": "https://example.com/article2",
        "title": "Xiaomi cuts Redmi Note 14 price in India",
        "content": "Xiaomi has reduced the price of its Redmi Note 14 by 10% in the Indian market amid heightened competition from budget rivals...",
        "published_date": "2025-04-01",
        "company_mentioned": "Xiaomi",
    },
    {
        "source": "Reuters",
        "url": "https://example.com/article3",
        "title": "Apple launches iPhone 16e as budget alternative",
        "content": "Apple unveiled the iPhone 16e, a lower-priced model aimed at competing with budget Android manufacturers in emerging markets...",
        "published_date": "2025-02-19",
        "company_mentioned": "Apple",
    },
]

REVIEWS = [
    {
        "product_name": "Redmi Note 14",
        "source": "Amazon",
        "review_text": "Great value for money, battery life is excellent but camera could be better in low light.",
        "rating": 4.2,
        "review_date": "2025-04-15",
    },
    {
        "product_name": "iPhone 16e",
        "source": "Amazon",
        "review_text": "Good performance for the price, but I wish it had a better display refresh rate.",
        "rating": 4.0,
        "review_date": "2025-03-01",
    },
    {
        "product_name": "Galaxy A55",
        "source": "BestBuy",
        "review_text": "Solid mid-range phone, the AMOLED screen is a standout feature at this price point.",
        "rating": 4.5,
        "review_date": "2025-03-25",
    },
]


def seed_articles():
    for a in ARTICLES:
        db.run_query(
            """
            INSERT INTO raw_articles (source, url, title, content, published_date, company_mentioned)
            VALUES (%(source)s, %(url)s, %(title)s, %(content)s, %(published_date)s, %(company_mentioned)s)
            """,
            a,
        )
    print(f"{len(ARTICLES)} articles inserted.")


def seed_reviews():
    for r in REVIEWS:
        db.run_query(
            """
            INSERT INTO raw_reviews (product_name, source, review_text, rating, review_date)
            VALUES (%(product_name)s, %(source)s, %(review_text)s, %(rating)s, %(review_date)s)
            """,
            r,
        )
    print(f"{len(REVIEWS)} reviews inserted.")


if __name__ == "__main__":
    seed_articles()
    seed_reviews()
    db.close()
    print("Postgres seeding complete.")