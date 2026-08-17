"""
Sets up Neo4j schema constraints and loads sample data
for the Market Intelligence Knowledge Graph.

Run with: python scripts/setup_knowledge_graph.py
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.utils.neo4j_connection import db

CONSTRAINTS = [
    "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT region_name IF NOT EXISTS FOR (r:Region) REQUIRE r.name IS UNIQUE",
    "CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE",
]

SAMPLE_COMPANIES = [
    {"name": "Samsung", "type": "competitor", "headquarters": "South Korea"},
    {"name": "Apple", "type": "competitor", "headquarters": "USA"},
    {"name": "Xiaomi", "type": "competitor", "headquarters": "China"},
    {"name": "OnePlus", "type": "competitor", "headquarters": "China"},
    {"name": "Google", "type": "competitor", "headquarters": "USA"},
]

SAMPLE_REGIONS = [
    {"name": "India", "market_type": "emerging"},
    {"name": "USA", "market_type": "mature"},
    {"name": "Europe", "market_type": "mature"},
    {"name": "Southeast Asia", "market_type": "emerging"},
]


def setup_constraints():
    for constraint in CONSTRAINTS:
        db.run_query(constraint)
    print("Constraints created.")


def load_sample_companies():
    for company in SAMPLE_COMPANIES:
        db.run_query(
            "MERGE (c:Company {name: $name}) "
            "SET c.type = $type, c.headquarters = $headquarters",
            company,
        )
    print(f"{len(SAMPLE_COMPANIES)} companies loaded.")


def load_sample_regions():
    for region in SAMPLE_REGIONS:
        db.run_query(
            "MERGE (r:Region {name: $name}) SET r.market_type = $market_type",
            region,
        )
    print(f"{len(SAMPLE_REGIONS)} regions loaded.")


def link_companies_to_regions():
    operations = [
        ("Samsung", "India"), ("Samsung", "USA"), ("Samsung", "Europe"),
        ("Apple", "USA"), ("Apple", "Europe"),
        ("Xiaomi", "India"), ("Xiaomi", "Southeast Asia"), ("Xiaomi", "Europe"),
        ("OnePlus", "India"), ("OnePlus", "Southeast Asia"),
        ("Google", "USA"), ("Google", "India"),
    ]
    for company, region in operations:
        db.run_query(
            "MATCH (c:Company {name: $company}), (r:Region {name: $region}) "
            "MERGE (c)-[:OPERATES_IN]->(r)",
            {"company": company, "region": region},
        )
    print(f"{len(operations)} OPERATES_IN relationships created.")


if __name__ == "__main__":
    setup_constraints()
    load_sample_companies()
    load_sample_regions()
    link_companies_to_regions()
    db.close()
    print("Knowledge graph setup complete.")
