"""
Adds Product and Event nodes to the Knowledge Graph, with dated events
to support the Trend & Forecasting Agent later.
Run with: python scripts/enrich_knowledge_graph.py
(Run setup_knowledge_graph.py first if you have not already.)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.neo4j_connection import db

PRODUCTS = [
    {"name": "Galaxy S25", "company": "Samsung", "category": "flagship", "launch_date": "2025-01-15", "price": 999},
    {"name": "Galaxy A55", "company": "Samsung", "category": "midrange", "launch_date": "2025-03-10", "price": 449},
    {"name": "iPhone 16", "company": "Apple", "category": "flagship", "launch_date": "2024-09-20", "price": 999},
    {"name": "iPhone 16e", "company": "Apple", "category": "budget", "launch_date": "2025-02-19", "price": 599},
    {"name": "Xiaomi 15", "company": "Xiaomi", "category": "flagship", "launch_date": "2024-11-01", "price": 899},
    {"name": "Redmi Note 14", "company": "Xiaomi", "category": "budget", "launch_date": "2025-01-05", "price": 249},
    {"name": "OnePlus 13", "company": "OnePlus", "category": "flagship", "launch_date": "2025-01-07", "price": 899},
    {"name": "Pixel 9", "company": "Google", "category": "flagship", "launch_date": "2024-08-13", "price": 799},
]

EVENTS = [
    {"company": "Xiaomi", "type": "price_change", "date": "2025-04-01", "description": "Redmi Note 14 price cut by 10% in India"},
    {"company": "Samsung", "type": "geographic_expansion", "date": "2025-03-20", "description": "Expanded Galaxy A-series retail presence in Southeast Asia"},
    {"company": "OnePlus", "type": "partnership", "date": "2025-02-10", "description": "Partnered with a regional telecom for bundled data plans"},
    {"company": "Google", "type": "technology_adoption", "date": "2025-01-20", "description": "Integrated on-device AI features across Pixel lineup"},
    {"company": "Apple", "type": "price_change", "date": "2025-02-19", "description": "Launched lower-priced iPhone 16e to counter budget competitors"},
]


def load_products():
    for p in PRODUCTS:
        db.run_query(
            "MERGE (prod:Product {name: $name}) "
            "SET prod.category = $category, prod.launch_date = date($launch_date), prod.price = $price "
            "WITH prod "
            "MATCH (c:Company {name: $company}) "
            "MERGE (c)-[:LAUNCHED]->(prod)",
            p,
        )
    print(f"{len(PRODUCTS)} products loaded and linked.")


def load_events():
    for i, e in enumerate(EVENTS):
        db.run_query(
            "MERGE (ev:Event {id: $id}) "
            "SET ev.type = $type, ev.date = date($date), ev.description = $description "
            "WITH ev "
            "MATCH (c:Company {name: $company}) "
            "MERGE (c)-[:INVOLVED_IN]->(ev)",
            {**e, "id": f"event_{i+1}"},
        )
    print(f"{len(EVENTS)} events loaded and linked.")


if __name__ == "__main__":
    load_products()
    load_events()
    db.close()
    print("Knowledge graph enrichment complete.")