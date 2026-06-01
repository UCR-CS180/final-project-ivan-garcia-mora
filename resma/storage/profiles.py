import sqlite3
import json
import uuid
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resma.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_profile(profile: dict) -> dict:
    """
    Save a validated student profile to the database.

    Expected profile fields:
        email, major, year, interests (list), skills (list)

    Returns:
        {"status": "success", "id": "student_xxx"}
        {"status": "exists", "message": "duplicate email"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        student_id = "student_" + str(uuid.uuid4())[:8]

        cursor.execute("""
            INSERT INTO students (id, email, major, year, interests, skills)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            profile["email"].strip().lower(),
            profile["major"].strip(),
            profile["year"].strip().lower(),
            json.dumps(profile["interests"]),
            json.dumps(profile["skills"])
        ))

        conn.commit()
        conn.close()
        return {"status": "success", "id": student_id}

    except sqlite3.IntegrityError:
        return {"status": "exists", "message": "an account with that email already exists"}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}


def get_profile(profile_id: str) -> dict:
    """
    Retrieve a student profile by ID.

    Returns:
        {"status": "success", "data": {...}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return {"status": "not_found"}

        return {
            "status": "success",
            "data": {
                "id": row["id"],
                "email": row["email"],
                "major": row["major"],
                "year": row["year"],
                "interests": json.loads(row["interests"]),
                "skills": json.loads(row["skills"])
            }
        }

    except Exception as e:
        return {"status": "db_error", "message": str(e)}


def get_profile_by_email(email: str) -> dict:
    """
    Retrieve a student profile by email.
    Useful for login or duplicate checks.

    Returns:
        {"status": "success", "data": {...}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return {"status": "not_found"}

        return {
            "status": "success",
            "data": {
                "id": row["id"],
                "email": row["email"],
                "major": row["major"],
                "year": row["year"],
                "interests": json.loads(row["interests"]),
                "skills": json.loads(row["skills"])
            }
        }

    except Exception as e:
        return {"status": "db_error", "message": str(e)}


def delete_profile(profile_id: str) -> dict:
    """
    Delete a student profile by ID.
    Useful for testing and cleanup.

    Returns:
        {"status": "success"}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM students WHERE id = ?", (profile_id,))
        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return {"status": "not_found"}

        conn.close()
        return {"status": "success"}

    except Exception as e:
        return {"status": "db_error", "message": str(e)}