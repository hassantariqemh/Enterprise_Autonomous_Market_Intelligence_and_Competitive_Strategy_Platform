"""
Fetches "public report" style coverage (earnings reports, annual reports,
financial results) via NewsAPI, covering the spec's "Public Reports" /
"Financial Reports" source type at a lightweight, news-coverage level.
Inserts into raw_articles, reusing the same downstream NLP pipeline.
Run with: python scripts/fetch_public_reports.py
"""
import sys
import os
import requests
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.postgres_connection import db

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
TRACKED_COMPANIES = ["Samsung", "Apple", "Xiaomi", "OnePlus", "Google", "Vivo", "Oppo", "Huawei", "Sony", "Motorola"]


def fetch_report_coverage(company: str, page_size: int = 3):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'{company} (earnings OR "annual report" OR "quarterly results")',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWSAPI_KEY,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("articles", [])


def article_already_exists(url: str) -> bool:
    rows = db.run_query(
        "SELECT id FROM raw_articles WHERE url = %(url)s", {"url": url}, fetch=True
    )
    return len(rows) > 0


def insert_article(company: str, article: dict):
    published = article.get("publishedAt", "")[:10] or datetime.now().strftime("%Y-%m-%d")
    db.run_query(
        """
        INSERT INTO raw_articles (source, url, title, content, published_date, company_mentioned)
        VALUES (%(source)s, %(url)s, %(title)s, %(content)s, %(published_date)s, %(company_mentioned)s)
        """,
        {
            "source": article.get("source", {}).get("name", "Public Report Coverage"),
            "url": article.get("url", ""),
            "title": article.get("title", ""),
            "content": article.get("description") or article.get("content") or "",
            "published_date": published,
            "company_mentioned": company,
        },
    )


def fetch_all():
    if not NEWSAPI_KEY:
        print("NEWSAPI_KEY not set in .env — aborting.")
        return

    total_inserted = 0
    for company in TRACKED_COMPANIES:
        articles = fetch_report_coverage(company)
        inserted = 0
        for article in articles:
            url = article.get("url", "")
            if not url or article_already_exists(url):
                continue
            insert_article(company, article)
            inserted += 1
            total_inserted += 1
        print(f"{company}: fetched {len(articles)}, inserted {inserted} new")

    print(f"\nDone. {total_inserted} new public-report-coverage articles inserted.")


if __name__ == "__main__":
    fetch_all()
    db.close()