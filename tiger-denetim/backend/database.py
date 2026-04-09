import pymssql
from config import settings


def get_connection(database: str = None):
    """SQL Server baglantisi olustur"""
    return pymssql.connect(
        server=settings.DB_SERVER,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=database or settings.DB_NAME,
    )


def execute_query(sql: str, database: str = None):
    """SQL calistir ve sonuc dondur"""
    conn = get_connection(database)
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
    finally:
        conn.close()
