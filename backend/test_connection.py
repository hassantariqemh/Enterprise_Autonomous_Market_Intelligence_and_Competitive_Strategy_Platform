from app.utils.neo4j_connection import db

result = db.run_query("RETURN 'Connection successful' AS message")
print(result)
db.close()