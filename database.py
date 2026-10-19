import sqlite3
from typing import Optional, List, Tuple
from models import LectureRevisionPack

DB_PATH = "revision_history.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lectures (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                pack_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_lecture_pack(video_id: str, pack: LectureRevisionPack):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO lectures (video_id, title, pack_json) VALUES (?, ?, ?)",
            (video_id, pack.lecture_title, pack.model_dump_json())
        )

def load_lecture_pack(video_id: str) -> Optional[LectureRevisionPack]:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT pack_json FROM lectures WHERE video_id = ?", (video_id,)
        ).fetchone()
        if row:
            return LectureRevisionPack.model_validate_json(row[0])
    return None

def list_saved_lectures() -> List[Tuple[str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT video_id, title FROM lectures ORDER BY created_at DESC"
        ).fetchall()