"""
Adds market events for the newly added competitor companies (Vivo, Oppo,
Huawei, Sony, Motorola), so Competitor Activity and Risk/Opportunity
scoring reflects them too, not just the original 5 companies.
Run with: python scripts/expand_events.py
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.neo4j_connection import db

NEW_EVENTS = [
    {"company": "Vivo", "type": "geographic_expansion", "date": "2025-03-15", "description": "Expanded Vivo X-series retail presence across South Asia"},
    {"company": "Oppo", "type": "price_change", "date": "2025-04-05", "description": "Oppo A3 price reduced by 8% in Southeast Asia"},
    {"company": "Huawei", "type": "technology_adoption", "date": "2025-01-25", "description": "Integrated proprietary AI chipset across Pura series"},
    {"company": "Sony", "type": "partnership", "date": "2025-02-15", "description": "Partnered with a camera sensor supplier for exclusive imaging tech"},
    {"company": "Motorola", "type": "price_change", "date": "2025-03-28", "description": "Edge 50 price cut by 12% ahead of new model launch"},
]


def add_events():
    existing = db.run_query("MATCH (e:Event) RETURN e.id AS id", {})
    existing_ids = {r["id"] for r in existing}
    next_index = len(existing_ids) + 1

    for i, e in enumerate(NEW_EVENTS):
        event_id = f"event_{next_index + i}"
        db.run_query(
            "MERGE (ev:Event {id: $id}) "
            "SET ev.type = $type, ev.date = date($date), ev.description = $description "
            "WITH ev "
            "MATCH (c:Company {name: $company}) "
            "MERGE (c)-[:INVOLVED_IN]->(ev)",
            {**e, "id": event_id},
        )
    print(f"{len(NEW_EVENTS)} events added/linked.")


if __name__ == "__main__":
    add_events()
    db.close()
    print("Event expansion complete.")