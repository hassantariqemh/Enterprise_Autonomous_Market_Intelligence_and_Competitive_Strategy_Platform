import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.utils.postgres_connection import db

result = db.run_query("SELECT version();", fetch=True)
print("Connected! PostgreSQL version:", result[0][0])
db.close()