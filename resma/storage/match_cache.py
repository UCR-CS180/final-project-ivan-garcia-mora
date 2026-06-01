import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resma.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_matches(profile_id: str, matches: list) -> dict:
    """
    Cache match results for a profile.
    Clears any previous matches for this profile before saving new ones.

    Returns:
        {"status": "success"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # clear old matches for this profile
        cursor.execute(
            "DELETE FROM match_cache WHERE profile_id = ?",
            (profile_id,)
        )

        for match in matches:
            cursor.execute("""
                INSERT INTO match_cache (profile_id, abstract_id, score, reason, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile_id,
                match["abstract_id"],
                match.get("rank"),
                match.get("reason", ""),
                datetime.utcnow().isoformat()
            ))

        conn.commit()
        conn.close()
        return {"status": "success"}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}


def get_cached_matches(profile_id: str) -> dict:
    """
    Retrieve cached matches for a profile ordered by rank.

    Returns:
        {"status": "success", "data": {"matches": [...]}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM match_cache
            WHERE profile_id = ?
            ORDER BY score ASC
        """, (profile_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"status": "not_found"}

        matches = [
            {
                "abstract_id": row["abstract_id"],
                "rank": int(row["score"]) if row["score"] else None,
                "reason": row["reason"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]
        return {"status": "success", "data": {"matches": matches}}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}


def clear_cache(profile_id: str) -> dict:
    """
    Delete all cached matches for a profile.
    Call this when a student updates their profile.

    Returns:
        {"status": "success"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM match_cache WHERE profile_id = ?",
            (profile_id,)
        )
        conn.commit()
        conn.close()
        return {"status": "success"}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}