"""
Fetches real SEC filing metadata (10-K, 10-Q, 8-K) from SEC EDGAR's public
submissions API for tracked companies that are US-listed and SEC-registered,
covering the spec's "Financial Reports" source type. Inserts a
filing-summary entry into raw_articles, reusing the same table and
downstream NLP pipeline as the other fetch scripts.
Run with: python scripts/fetch_financial_reports.py

Note: SEC EDGAR only covers US-listed, SEC-registered companies. Of the
10 tracked companies, only Apple and Google file with the SEC. The rest
(Samsung, Xiaomi, OnePlus, Vivo, Oppo, Huawei, Sony, Motorola) are not
SEC-registered in a way this endpoint covers, so no data is fabricated
for them — they are simply skipped.
"""
import sys
import os
import requests
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.postgres_connection import db

# SEC requires a descriptive User-Agent identifying the requester
HEADERS = {"User-Agent": "market-intel-platform student-case-study contact: hassan@example.com"}

# CIK (Central Index Key) numbers for tracked companies that are SEC-registered
CIK_MAP = {
    "Apple": "0000320193",
    "Google": "0001652044",  # Alphabet Inc.
}

RELEVANT_FORMS = {"10-K", "10-Q", "8-K"}


def fetch_filings(company: str, cik: str, limit: int = 5):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    results = []
    for i, form in enumerate(forms):
        if form in RELEVANT_FORMS:
            results.append({
                "form": form,
                "date": dates[i],
                "accession": accession_numbers[i],
                "doc": primary_docs[i],
            })
        if len(results) >= limit:
            break
    return results


def article_already_exists(url: str) -> bool:
    rows = db.run_query(
        "SELECT id FROM raw_articles WHERE url = %(url)s", {"url": url}, fetch=True
    )
    return len(rows) > 0


def insert_filing(company: str, cik: str, filing: dict):
    accession_no_dashes = filing["accession"].replace("-", "")
    filing_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession_no_dashes}/{filing['doc']}"
    )

    if article_already_exists(filing_url):
        return False

    title = f"{company} SEC Filing: {filing['form']} filed {filing['date']}"
    content = (
        f"Official SEC EDGAR filing for {company}. Form type: {filing['form']}. "
        f"Filed on {filing['date']}. Accession number: {filing['accession']}."
    )

    db.run_query(
        """
        INSERT INTO raw_articles (source, url, title, content, published_date, company_mentioned)
        VALUES (%(source)s, %(url)s, %(title)s, %(content)s, %(published_date)s, %(company_mentioned)s)
        """,
        {
            "source": "SEC EDGAR",
            "url": filing_url,
            "title": title,
            "content": content,
            "published_date": filing["date"],
            "company_mentioned": company,
        },
    )
    return True


def fetch_all():
    total_inserted = 0
    for company, cik in CIK_MAP.items():
        try:
            filings = fetch_filings(company, cik)
        except requests.RequestException as e:
            print(f"{company}: fetch failed ({e})")
            continue

        inserted = 0
        for filing in filings:
            if insert_filing(company, cik, filing):
                inserted += 1
                total_inserted += 1
        print(f"{company}: found {len(filings)} recent filings, inserted {inserted} new")

    skipped = [c for c in ["Samsung", "Xiaomi", "OnePlus", "Vivo", "Oppo", "Huawei", "Sony", "Motorola"]]
    print(f"\nSkipped (not SEC-registered / not covered by this endpoint): {', '.join(skipped)}")
    print(f"Done. {total_inserted} new SEC filing records inserted into raw_articles.")


if __name__ == "__main__":
    fetch_all()
    db.close()