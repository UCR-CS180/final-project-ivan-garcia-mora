import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "researchmatch.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_email_history_table():
    """
    Create the email_history table if it doesn't exist.
    Call this once from init_db.py or on first use.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_history (
            id          TEXT PRIMARY KEY,
            profile_id  TEXT NOT NULL,
            abstract_id TEXT NOT NULL,
            subject     TEXT NOT NULL,
            body        TEXT NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_email_draft(profile_id: str, abstract_id: str, subject: str, body: str) -> dict:
    """
    Save a generated email draft to history.

    Returns:
        {"status": "success", "id": "email_xxx"}
        {"status": "db_error", "message": "..."}
    """
    try:
        init_email_history_table()
        conn = get_connection()
        cursor = conn.cursor()

        email_id = "email_" + str(uuid.uuid4())[:8]

        cursor.execute("""
            INSERT INTO email_history (id, profile_id, abstract_id, subject, body, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            email_id,
            profile_id,
            abstract_id,
            subject,
            body,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()
        return {"status": "success", "id": email_id}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}


def get_email_history(profile_id: str) -> dict:
    """
    Retrieve all saved email drafts for a student, newest first.

    Returns:
        {"status": "success", "data": [...]}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try:
        init_email_history_table()
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM email_history
            WHERE profile_id = ?
            ORDER BY created_at DESC
        """, (profile_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"status": "not_found"}

        drafts = [
            {
                "id": row["id"],
                "abstract_id": row["abstract_id"],
                "subject": row["subject"],
                "body": row["body"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]
        return {"status": "success", "data": drafts}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}