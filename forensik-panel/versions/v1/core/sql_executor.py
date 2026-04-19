"""SQL çalıştırma — pymssql + Polars"""
import logging
import re
import time

import polars as pl

from core.db import get_connection

logger = logging.getLogger(__name__)

DANGEROUS_KEYWORDS = [
    "INSERT ", "UPDATE ", "DELETE ", "DROP ", "TRUNCATE ",
    "ALTER ", "EXEC ", "EXECUTE ", "CREATE ", "MERGE ",
    "GRANT ", "REVOKE ", "SHUTDOWN",
]

_COMMENT_RE = re.compile(r"--[^\n]*|/\*.*?\*/", re.DOTALL)


def _strip_comments(sql: str) -> str:
    return _COMMENT_RE.sub(" ", sql)


def validate_sql(sql: str) -> tuple[bool, str]:
    """SQL güvenlik kontrolü — sadece SELECT izinli"""
    if not sql or not sql.strip():
        return False, "SQL sorgusu boş"

    cleaned = _strip_comments(sql).upper()

    for kw in DANGEROUS_KEYWORDS:
        if kw in cleaned:
            return False, f"Yasak komut: {kw.strip()}. Sadece SELECT sorguları çalıştırılabilir."

    if "SELECT" not in cleaned:
        return False, "SELECT içermeyen sorgular desteklenmez"

    return True, ""


def execute_sql(database: str, sql: str, timeout: int = 600) -> tuple[pl.DataFrame, float]:
    """SQL çalıştırır, Polars DataFrame ve süre döndürür"""
    ok, err = validate_sql(sql)
    if not ok:
        raise ValueError(err)

    logger.info(f"SQL çalıştırılıyor [{database}]: {sql[:150]}...")
    start = time.time()

    with get_connection(database, timeout=timeout) as conn:
        cur = conn.cursor()
        cur.execute(sql)

        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()

    duration = time.time() - start
    logger.info(f"SQL tamamlandı: {len(rows)} satır, {duration:.2f} sn")

    if rows and columns:
        data = [dict(zip(columns, row)) for row in rows]
        df = pl.DataFrame(data, infer_schema_length=1000)
    else:
        df = pl.DataFrame(schema={col: pl.Utf8 for col in columns})

    return df, duration
