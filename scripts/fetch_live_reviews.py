"""
Fetches live review-style content from NewsAPI (searching for review
articles) for tracked products and inserts them into raw_reviews (same
table the manual seed script and process_reviews.py already use).
Reuses the same NEWSAPI_KEY already configured for fetch_live_articles.py.
Run with: python scripts/fetch_live_reviews.py
"""
import sys
import os
import requests
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.postgres_connection import db

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

TRACKED_PRODUCTS = [
    "Galaxy S25", "Galaxy A55", "iPhone 16", "iPhone 16e",
    "Xiaomi 15", "Redmi Note 14", "OnePlus 13", "Pixel 9",
    "Vivo X200", "Vivo Y29", "Oppo Find X8", "Oppo A3",
    "Huawei Pura 70", "Sony Xperia 1 VI", "Motorola Edge 50",
]


def fetch_review_articles(product: str, page_size: int = 3):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'"{product}" review',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWSAPI_KEY,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("articles", [])


def review_already_exists(source_url: str) -> bool:
    rows = db.run_query(
        "SELECT id FROM raw_reviews WHERE source = %(source)s", {"source": source_url}, fetch=True
    )
    return len(rows) > 0


def insert_review(product: str, article: dict):
    text = article.get("description") or article.get("content") or article.get("title") or ""
    if not text:
        return False

    published = article.get("publishedAt", "")[:10] or datetime.now().strftime("%Y-%m-%d")

    db.run_query(
        """
        INSERT INTO raw_reviews (product_name, source, review_text, rating, review_date)
        VALUES (%(product_name)s, %(source)s, %(review_text)s, %(rating)s, %(review_date)s)
        """,
        {
            "product_name": product,
            "source": article.get("url", ""),
            "review_text": text[:2000],
            "rating": None,
            "review_date": published,
        },
    )
    return True


def fetch_all():
    if not NEWSAPI_KEY:
        print("NEWSAPI_KEY not set in .env — aborting.")
        return

    total_inserted = 0
    for product in TRACKED_PRODUCTS:
        try:
            articles = fetch_review_articles(product)
        except requests.RequestException as e:
            print(f"{product}: fetch failed ({e})")
            continue

        inserted_for_product = 0
        for article in articles:
            url = article.get("url", "")
            if not url or review_already_exists(url):
                continue
            if insert_review(product, article):
                inserted_for_product += 1
                total_inserted += 1

        print(f"{product}: fetched {len(articles)}, inserted {inserted_for_product} new")

    print(f"\nDone. {total_inserted} new live review-style items inserted into raw_reviews.")


if __name__ == "__main__":
    fetch_all()
    db.close()