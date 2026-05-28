import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resma.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_abstracts() -> dict:
    """
    Retrieve all research abstracts from the database.
 
    Returns:
        {"status": "success", "data": [{"id": ..., "title": ..., ...}, ...]}
        {"status": "no_abstracts"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM abstracts")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"status", "no_abstracts"}
        
        abstracts = [_row_to_dict(row) for row in rows]
        return {"status": "success", "data": abstracts}
    except Exception as e:
        return {"status": "db_error", "message": str(e)}
    
def get_abstracts_by_id(abstract_id: str) -> dict:
    """
    Retrieve a single research abstract by ID.
 
    Returns:
        {"status": "success", "data": {"id": ..., "title": ..., "text": ..., ...}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try: 
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM abstracts WHERE LOWER(department) = ?",
            (department.strip().lower(),)
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return{"status": "no_abstracts"}

        abstracts = [_row_to_dict(row) for row in rows]
        return {"status": "success", "data": abstracts}
    except Exception as e:
        return {"status": "db_error", "message": str(e)}
    
def get_abstract_by_id(abstract_id: str) -> dict:
    """
    Retrieve a single research abstract by ID.
 
    Returns:
        {"status": "success", "data": {"id": ..., "title": ..., "text": ..., ...}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM abstracts WHERE id = ?", (abstract_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return {"status": "success", "data": _row_to_dict(row)}
        
        return {"status": "success", "data": _row_to_dict(row)}
    except Exception as e:
        return {"status": "db_error", "message": str(e)}
    
def get_abstracts_by_department(department: str) -> dict:
    """
    Retrieve all abstracts for a given department.
    Useful for narrowing matches before sending to Gemini.
 
    Returns:
        {"status": "success", "data": [...]}
        {"status": "no_abstracts"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
 
        cursor.execute(
            "SELECT * FROM abstracts WHERE LOWER(department) = ?",
            (department.strip().lower(),)
        )
        rows = cursor.fetchall()
        conn.close()
 
        if not rows:
            return {"status": "no_abstracts"}
 
        return {"status": "success", "data": [_row_to_dict(row) for row in rows]}
 
    except Exception as e:
        return {"status": "db_error", "message": str(e)}
 
 
def search_abstracts_by_keyword(keyword: str) -> dict:
    """
    Search abstracts whose keywords or text contain the given term.
    Simple text search — Gemini handles the semantic matching later.
 
    Returns:
        {"status": "success", "data": [...]}
        {"status": "no_abstracts"}
        {"status": "db_error", "message": "..."}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
 
        term = f"%{keyword.strip().lower()}%"
        cursor.execute("""
            SELECT * FROM abstracts
            WHERE LOWER(keywords) LIKE ?
               OR LOWER(text) LIKE ?
               OR LOWER(title) LIKE ?
        """, (term, term, term))
        rows = cursor.fetchall()
        conn.close()
 
        if not rows:
            return {"status": "no_abstracts"}
 
        return {"status": "success", "data": [_row_to_dict(row) for row in rows]}
 
    except Exception as e:
        return {"status": "db_error", "message": str(e)}
 
 
def _row_to_dict(row) -> dict:
    """
    Convert a sqlite3.Row to a plain dict,
    parsing the JSON keywords field back into a list.
    """
    return {
        "id": row["id"],
        "title": row["title"],
        "professor": row["professor"],
        "lab": row["lab"],
        "department": row["department"],
        "keywords": json.loads(row["keywords"]) if row["keywords"] else [],
        "text": row["text"]
    }