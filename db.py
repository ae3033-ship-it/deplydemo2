import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg2

load_dotenv(Path(__file__).parent / ".env")


def get_student_names():
    url = os.environ["DATABASE_URL"]
    if "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM student ORDER BY id")
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()
