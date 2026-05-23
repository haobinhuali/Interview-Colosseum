import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "interview.db")


def _ensure_db_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id TEXT PRIMARY KEY,
            parsed_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            resume_id TEXT NOT NULL,
            job_type TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'INIT',
            current_round INTEGER NOT NULL DEFAULT 0,
            profile_data TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
        )
    """)
    conn.commit()
    conn.close()


def save_resume(resume_id: str, parsed_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO resumes (resume_id, parsed_data) VALUES (?, ?)",
        (resume_id, json.dumps(parsed_data, ensure_ascii=False))
    )
    conn.commit()
    conn.close()


def get_resume(resume_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT parsed_data FROM resumes WHERE resume_id = ?", (resume_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["parsed_data"])
    return None


def save_session(session_id: str, resume_id: str, job_type: str, stage: str, current_round: int, profile_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO sessions (session_id, resume_id, job_type, stage, current_round, profile_data) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, resume_id, job_type, stage, current_round, json.dumps(profile_data, ensure_ascii=False))
    )
    conn.commit()
    conn.close()


def get_session(session_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "session_id": row["session_id"],
            "resume_id": row["resume_id"],
            "job_type": row["job_type"],
            "stage": row["stage"],
            "current_round": row["current_round"],
            "profile_data": json.loads(row["profile_data"])
        }
    return None


init_db()
