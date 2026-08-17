"""
Uses NetworkX to compute graph-level metrics on top of the Neo4j knowledge
graph (e.g. which company is most "central"/connected in the competitive
landscape based on shared product categories and price tiers).
"""
from itertools import combinations
import networkx as nx
from app.utils.neo4j_connection import db


def price_tier(price):
    if price is None:
        return "unknown"
    if price < 400:
        return "budget"
    if price < 800:
        return "midrange"
    return "flagship_tier"


def build_competitor_graph():
    """
    Builds an undirected NetworkX graph where companies are connected if
    they compete in the same product category and/or price tier. Edge
    weight reflects how many attributes two companies share.
    """
    G = nx.Graph()

    companies = db.run_query("MATCH (c:Company) RETURN c.name AS name", {})
    for c in companies:
        G.add_node(c["name"])

    products = db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product) "
        "RETURN c.name AS company, p.category AS category, p.price AS price",
        {},
    )

    for p1, p2 in combinations(products, 2):
        if p1["company"] == p2["company"]:
            continue

        shared = 0
        reasons = []

        if p1["category"] == p2["category"]:
            shared += 1
            reasons.append(f"category:{p1['category']}")

        if price_tier(p1["price"]) == price_tier(p2["price"]):
            shared += 1
            reasons.append(f"price_tier:{price_tier(p1['price'])}")

        if shared > 0:
            a, b = sorted([p1["company"], p2["company"]])
            if G.has_edge(a, b):
                G[a][b]["weight"] += shared
                G[a][b]["reasons"] = list(set(G[a][b]["reasons"] + reasons))
            else:
                G.add_edge(a, b, weight=shared, reasons=reasons)

    return G


def get_competitive_centrality():
    """
    Returns companies ranked by weighted centrality in the competitive
    graph — higher centrality means a company overlaps (by category and/or
    price tier) with more competitors across more dimensions, indicating a
    more contested competitive position.
    """
    G = build_competitor_graph()

    if G.number_of_edges() == 0:
        return {
            "status": "insufficient_data",
            "message": "Not enough shared-category or shared-price-tier links "
                       "between companies to compute centrality.",
        }

    weighted_centrality = {
        node: sum(data["weight"] for _, _, data in G.edges(node, data=True))
        for node in G.nodes()
    }
    max_score = max(weighted_centrality.values()) or 1

    ranked = sorted(
        [
            {
                "company": name,
                "centrality_score": round(score / max_score, 3),
                "raw_shared_links": score,
            }
            for name, score in weighted_centrality.items()
        ],
        key=lambda x: -x["centrality_score"],
    )

    return {
        "status": "ok",
        "method": "weighted degree centrality over a graph where companies are "
                  "linked by shared product category and/or price tier "
                  "(normalized against the most-contested company)",
        "rankings": ranked,
    }