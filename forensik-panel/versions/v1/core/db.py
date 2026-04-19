"""SQL Server bağlantı — pymssql kullanır (pyodbc DEĞİL)"""
import logging
from contextlib import contextmanager

import pymssql

from config import CONFIG, get_sql_creds

logger = logging.getLogger(__name__)


@contextmanager
def get_connection(database: str, timeout: int = 600):
    """Bağlantı context manager'ı"""
    user, password = get_sql_creds()
    host = CONFIG["sql_server"]["host"]
    port = CONFIG["sql_server"]["port"]

    logger.info(f"SQL bağlantı açılıyor: {host}:{port}/{database}")

    conn = None
    try:
        conn = pymssql.connect(
            server=host,
            port=port,
            user=user,
            password=password,
            database=database,
            timeout=timeout,
            login_timeout=30,
            charset="UTF-8",
            as_dict=False,
        )
        yield conn
    finally:
        if conn:
            conn.close()
            logger.debug("SQL bağlantı kapatıldı")


def test_connection(database: str = None) -> dict:
    """Bağlantı testi"""
    db = database or CONFIG["sql_server"]["default_database"]
    try:
        with get_connection(db, timeout=10) as conn:
            cur = conn.cursor()
            cur.execute("SELECT @@VERSION, DB_NAME(), GETDATE()")
            row = cur.fetchone()
            return {
                "status": "ok",
                "database": db,
                "version": str(row[0])[:80],
                "current_db": str(row[1]),
                "server_time": str(row[2]),
            }
    except Exception as e:
        logger.exception(f"Bağlantı testi başarısız: {db}")
        return {
            "status": "error",
            "database": db,
            "error": str(e),
        }


def list_user_tables(database: str, limit: int = 500) -> list[dict]:
    """Veritabanındaki kullanıcı tablolarını listele"""
    sql = """
    SELECT TOP (%d)
        s.name AS schema_name,
        t.name AS table_name,
        p.rows AS row_count
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0,1)
    WHERE t.is_ms_shipped = 0
    ORDER BY s.name, t.name
    """ % limit
    with get_connection(database, timeout=30) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return [
            {"schema": r[0], "table": r[1], "rows": r[2]}
            for r in cur.fetchall()
        ]
