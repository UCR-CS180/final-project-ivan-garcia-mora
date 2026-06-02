import sqlite3
import json
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resma.db")
ABSTRACTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "abstracts.json")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id        TEXT PRIMARY KEY,
            email     TEXT UNIQUE NOT NULL,
            major     TEXT NOT NULL,
            year      TEXT NOT NULL,
            interests TEXT NOT NULL,
            skills    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS abstracts (
            id         TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            professor  TEXT,
            lab        TEXT,
            department TEXT,
            keywords   TEXT,
            text       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS match_cache (
            profile_id  TEXT NOT NULL,
            abstract_id TEXT NOT NULL,
            score       REAL,
            reason      TEXT,
            created_at  TEXT,
            PRIMARY KEY (profile_id, abstract_id)
        );
    """)
    conn.commit()
    print("Tables created.")

def seed_abstracts(conn):
    if not os.path.exists(ABSTRACTS_PATH):
        print(f"No abstracts.json found at {ABSTRACTS_PATH} - skipping seed.")
        return
    with open(ABSTRACTS_PATH, "r", encoding="utf-8") as f:
        abstracts = json.load(f)

    cursor = conn.cursor()
    inserted = 0
    skipped = 0

    for abstract in abstracts:
        try:
            text = abstract["text"]
            if isinstance(text, list):
                text = " ".join(text)
            cursor.execute("""
                INSERT INTO abstracts (id, title, professor, lab, department, keywords, text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                abstract.get("id", str(uuid.uuid4())),
                abstract["title"],
                abstract.get("professor", ""),
                abstract.get("lab", ""),
                abstract.get("department", ""),
                json.dumps(abstract.get("keywords", [])),
                text,
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    print(f"Abstracts seeded: {inserted} inserted, {skipped} already existed.")

if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)
    seed_abstracts(conn)
    conn.close()
    print(f"Database ready at: {os.path.abspath(DB_PATH)}")
    
from storage.email_history import init_email_history_table
init_email_history_table()