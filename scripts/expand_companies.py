"""
Adds additional competitor companies and their products to the Knowledge
Graph, expanding coverage beyond the original 5 tracked companies.
Run with: python scripts/expand_companies.py
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.neo4j_connection import db

NEW_COMPANIES = [
    {"name": "Vivo", "headquarters": "China"},
    {"name": "Oppo", "headquarters": "China"},
    {"name": "Huawei", "headquarters": "China"},
    {"name": "Sony", "headquarters": "Japan"},
    {"name": "Motorola", "headquarters": "USA"},
]

NEW_PRODUCTS = [
    {"name": "Vivo X200", "company": "Vivo", "category": "flagship", "launch_date": "2025-01-10", "price": 899},
    {"name": "Vivo Y29", "company": "Vivo", "category": "budget", "launch_date": "2025-03-01", "price": 199},
    {"name": "Oppo Find X8", "company": "Oppo", "category": "flagship", "launch_date": "2024-12-15", "price": 949},
    {"name": "Oppo A3", "company": "Oppo", "category": "budget", "launch_date": "2025-02-05", "price": 179},
    {"name": "Huawei Pura 70", "company": "Huawei", "category": "flagship", "launch_date": "2025-01-20", "price": 899},
    {"name": "Sony Xperia 1 VI", "company": "Sony", "category": "flagship", "launch_date": "2024-11-05", "price": 1099},
    {"name": "Motorola Edge 50", "company": "Motorola", "category": "midrange", "launch_date": "2025-02-20", "price": 499},
]


def add_companies():
    for c in NEW_COMPANIES:
        db.run_query(
            "MERGE (co:Company {name: $name}) "
            "SET co.type = 'competitor', co.headquarters = $headquarters",
            c,
        )
    print(f"{len(NEW_COMPANIES)} companies added/merged.")


def add_products():
    for p in NEW_PRODUCTS:
        db.run_query(
            "MERGE (prod:Product {name: $name}) "
            "SET prod.category = $category, prod.launch_date = date($launch_date), prod.price = $price "
            "WITH prod "
            "MATCH (c:Company {name: $company}) "
            "MERGE (c)-[:LAUNCHED]->(prod)",
            p,
        )
    print(f"{len(NEW_PRODUCTS)} products added/linked.")


if __name__ == "__main__":
    add_companies()
    add_products()
    db.close()
    print("Company expansion complete.")