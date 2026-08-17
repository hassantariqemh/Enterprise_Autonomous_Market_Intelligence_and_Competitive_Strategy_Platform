from app.utils.neo4j_connection import db


def get_all_competitors():
    query = "MATCH (c:Company) RETURN c.name AS name, c.type AS type, c.headquarters AS headquarters"
    return db.run_query(query)


def get_competitor_profile(name: str):
    query = """
    MATCH (c:Company {name: $name})
    OPTIONAL MATCH (c)-[:OPERATES_IN]->(r:Region)
    RETURN c.name AS name, c.type AS type, c.headquarters AS headquarters,
           COLLECT(r.name) AS regions
    """
    result = db.run_query(query, {"name": name})
    return result[0] if result else None


def companies_by_region_count():
    query = """
    MATCH (c:Company)-[:OPERATES_IN]->(r:Region)
    RETURN c.name AS name, COUNT(r) AS region_count
    ORDER BY region_count DESC
    """
    return db.run_query(query)
