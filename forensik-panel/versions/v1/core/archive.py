"""DuckDB tabanlı arşiv"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import duckdb
import polars as pl

from config import CONFIG, DATA_DIR

logger = logging.getLogger(__name__)


def _is_windows_abs(p: str) -> bool:
    """C:/... veya C:\\... formatını tanı"""
    return len(p) >= 3 and p[1] == ":" and p[2] in ("/", "\\")


def _archive_paths():
    """Konfigdeki yolları doğrula — Windows'ta config yolu, yoksa yerel fallback"""
    import os

    configured_db_str = CONFIG["arsiv"]["duckdb_path"]
    configured_parquet_str = CONFIG["arsiv"]["parquet_dir"]

    # Windows-mutlak yol + Linux/Mac = fallback
    if _is_windows_abs(configured_db_str) and os.name != "nt":
        db_path = DATA_DIR / "archive" / "archive.duckdb"
        parquet_dir = DATA_DIR / "archive" / "results"
    else:
        db_path = Path(configured_db_str)
        parquet_dir = Path(configured_parquet_str)

    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        parquet_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        db_path = DATA_DIR / "archive" / "archive.duckdb"
        parquet_dir = DATA_DIR / "archive" / "results"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        parquet_dir.mkdir(parents=True, exist_ok=True)

    return db_path, parquet_dir


def _get_conn():
    duckdb_path, _ = _archive_paths()
    conn = duckdb.connect(str(duckdb_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            title VARCHAR,
            description VARCHAR,
            sql_text VARCHAR NOT NULL,
            database VARCHAR NOT NULL,
            row_count BIGINT,
            duration_sec DOUBLE,
            status VARCHAR,
            error_message VARCHAR,
            parquet_path VARCHAR
        )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS query_id_seq START 1")
    return conn


def save_query(
    title: str,
    description: str,
    sql: str,
    database: str,
    df: Optional[pl.DataFrame],
    duration: float,
    status: str,
    error_message: str = "",
) -> int:
    """Sorguyu arşive kaydet, query_id döndür"""
    _, parquet_dir = _archive_paths()
    conn = _get_conn()

    try:
        next_id = conn.execute("SELECT nextval('query_id_seq')").fetchone()[0]

        parquet_path = ""
        row_count = 0
        if status == "success" and df is not None and len(df) > 0:
            parquet_path = str(parquet_dir / f"q_{next_id:06d}.parquet")
            df.write_parquet(parquet_path)
            row_count = len(df)

        conn.execute("""
            INSERT INTO query_history
            (id, timestamp, title, description, sql_text, database,
             row_count, duration_sec, status, error_message, parquet_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            int(next_id),
            datetime.now(),
            title,
            description,
            sql,
            database,
            row_count,
            duration,
            status,
            error_message,
            parquet_path,
        ])

        logger.info(f"Arşive kaydedildi: #{next_id} — {title}")
        return int(next_id)
    finally:
        conn.close()


def get_query(query_id: int) -> Optional[dict]:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT id, timestamp, title, description, sql_text, database, "
            "row_count, duration_sec, status, error_message, parquet_path "
            "FROM query_history WHERE id = ?",
            [query_id],
        ).fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "timestamp": str(row[1]),
            "title": row[2],
            "description": row[3],
            "sql": row[4],
            "database": row[5],
            "row_count": row[6],
            "duration_sec": row[7],
            "status": row[8],
            "error_message": row[9],
            "parquet_path": row[10],
        }
    finally:
        conn.close()


def get_query_df(query_id: int) -> Optional[pl.DataFrame]:
    """Sorgu sonucunu Polars DataFrame olarak getir"""
    query = get_query(query_id)
    if not query or not query["parquet_path"]:
        return None

    path = Path(query["parquet_path"])
    if not path.exists():
        return None

    return pl.read_parquet(path)


def list_recent_queries(limit: int = 10) -> list[dict]:
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT id, timestamp, title, database, row_count, duration_sec, status
            FROM query_history
            ORDER BY id DESC
            LIMIT ?
        """, [limit]).fetchall()

        return [{
            "id": r[0],
            "timestamp": str(r[1]),
            "title": r[2],
            "database": r[3],
            "row_count": r[4],
            "duration_sec": r[5],
            "status": r[6],
        } for r in rows]
    finally:
        conn.close()


def list_all_queries(
    search: str = "",
    database: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[dict]:
    conn = _get_conn()
    try:
        query = """
            SELECT id, timestamp, title, database, row_count,
                   duration_sec, status, sql_text
            FROM query_history
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (LOWER(title) LIKE ? OR LOWER(sql_text) LIKE ?)"
            s = f"%{search.lower()}%"
            params.extend([s, s])

        if database:
            query += " AND database = ?"
            params.append(database)

        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)

        if date_to:
            query += " AND timestamp <= ?"
            params.append(date_to + " 23:59:59")

        query += " ORDER BY id DESC"

        rows = conn.execute(query, params).fetchall()

        return [{
            "id": r[0],
            "timestamp": str(r[1]),
            "title": r[2],
            "database": r[3],
            "row_count": r[4],
            "duration_sec": r[5],
            "status": r[6],
            "sql_preview": (r[7] or "")[:100],
        } for r in rows]
    finally:
        conn.close()


def count_queries() -> int:
    conn = _get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
    finally:
        conn.close()


def delete_query(query_id: int) -> bool:
    query = get_query(query_id)
    if not query:
        return False

    if query["parquet_path"]:
        path = Path(query["parquet_path"])
        if path.exists():
            path.unlink()

    conn = _get_conn()
    try:
        conn.execute("DELETE FROM query_history WHERE id = ?", [query_id])
        logger.info(f"Arşiv silindi: #{query_id}")
        return True
    finally:
        conn.close()
