import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "marketintel_raw"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

    def run_query(self, query, params=None, fetch=False):
        with self.conn.cursor() as cur:
            cur.execute(query, params or {})
            if fetch:
                return cur.fetchall()
            self.conn.commit()

    def close(self):
        self.conn.close()


db = PostgresDB()