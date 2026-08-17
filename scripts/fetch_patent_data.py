"""
Fetches real patent search results from Google Patents' public search
endpoint (used internally by patents.google.com's own search UI) for
tracked companies, covering the spec's "Patent Databases" source type.
Inserts into raw_articles, reusing the same table and downstream NLP
pipeline as the other fetch scripts.
Run with: python scripts/fetch_patent_data.py

Note: this uses an undocumented, public endpoint. If Google changes or
blocks it (similar to what happened with Reddit's API), each company's
request fails independently and is skipped — the rest of the pipeline
continues normally.
"""
import sys
import os
import requests
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.postgres_connection import db

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

TRACKED_COMPANIES = [
    "Samsung", "Apple", "Xiaomi", "OnePlus", "Google",
    "Vivo", "Oppo", "Huawei", "Sony", "Motorola",
]


def fetch_patents(company: str, limit: int = 3):
    url = "https://patents.google.com/xhr/query"
    params = {"url": f"q={company}+smartphone", "exp": "", "content": "1"}
    response = requests.get(url, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = data.get("results", {}).get("cluster", [])
    patents = []
    for cluster in results:
        for item in cluster.get("result", []):
            patent = item.get("patent", {})
            if patent:
                patents.append(patent)
            if len(patents) >= limit:
                return patents
    return patents


def article_already_exists(url: str) -> bool:
    rows = db.run_query(
        "SELECT id FROM raw_articles WHERE url = %(url)s", {"url": url}, fetch=True
    )
    return len(rows) > 0


def insert_patent(company: str, patent: dict):
    publication_number = patent.get("publication_number", "")
    if not publication_number:
        return False

    patent_url = f"https://patents.google.com/patent/{publication_number}"
    if article_already_exists(patent_url):
        return False

    title = patent.get("title", f"{company} patent filing")
    snippet = patent.get("snippet", "")
    filing_date = patent.get("filing_date", "") or datetime.now().strftime("%Y-%m-%d")

    db.run_query(
        """
        INSERT INTO raw_articles (source, url, title, content, published_date, company_mentioned)
        VALUES (%(source)s, %(url)s, %(title)s, %(content)s, %(published_date)s, %(company_mentioned)s)
        """,
        {
            "source": "Google Patents",
            "url": patent_url,
            "title": title,
            "content": snippet or f"Patent filing related to {company}.",
            "published_date": filing_date,
            "company_mentioned": company,
        },
    )
    return True


def fetch_all():
    total_inserted = 0
    for company in TRACKED_COMPANIES:
        try:
            patents = fetch_patents(company)
        except requests.RequestException as e:
            print(f"{company}: fetch failed ({e})")
            continue
        except ValueError as e:
            # JSON decoding failed — endpoint returned something unexpected
            print(f"{company}: could not parse response ({e})")
            continue

        inserted = 0
        for patent in patents:
            if insert_patent(company, patent):
                inserted += 1
                total_inserted += 1
        print(f"{company}: found {len(patents)} patents, inserted {inserted} new")

    print(f"\nDone. {total_inserted} new patent records inserted into raw_articles.")


if __name__ == "__main__":
    fetch_all()
    db.close()