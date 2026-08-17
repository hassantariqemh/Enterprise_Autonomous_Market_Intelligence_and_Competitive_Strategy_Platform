"""
Runs a full live-data update cycle: fetches new articles, industry
publication coverage, public-report coverage, SEC financial filings,
patent data, and reviews, then processes all of it through the existing
NLP pipelines. Designed to be run periodically via Windows Task
Scheduler for near-real-time updates.
Run with: python scripts/live_update_cycle.py
"""
import subprocess
import sys
import os
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(__file__)
PYTHON = sys.executable


def run_step(script_name: str):
    path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n[{datetime.now().isoformat()}] Running {script_name}...")
    result = subprocess.run([PYTHON, path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR in {script_name}:\n{result.stderr}")
    return result.returncode == 0


if __name__ == "__main__":
    print(f"=== Live update cycle started: {datetime.now().isoformat()} ===")

    steps = [
        "fetch_live_articles.py",
        "fetch_industry_publications.py",
        "fetch_public_reports.py",
        "fetch_financial_reports.py",
        "fetch_patent_data.py",
        "process_articles.py",
        "fetch_live_reviews.py",
        "process_reviews.py",
    ]

    results = {}
    for step in steps:
        results[step] = run_step(step)

    print("\n=== Cycle complete ===")
    for step, ok in results.items():
        print(f"  {step}: {'OK' if ok else 'FAILED'}")