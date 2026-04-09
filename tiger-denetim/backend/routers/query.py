import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import execute_query

router = APIRouter()

FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "EXEC",
    "EXECUTE",
    "xp_",
    "sp_",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
]


def validate_query(sql: str) -> bool:
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        return False
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword.upper() in sql_upper:
            return False
    return True


class QueryRequest(BaseModel):
    sql: str
    database: str = "TIGERDB"


@router.post("/query")
def run_query(req: QueryRequest):
    """Kullanicinin yazdigi SQL'i calistir (sadece SELECT)"""
    if not validate_query(req.sql):
        raise HTTPException(
            status_code=400,
            detail="Sadece SELECT sorgularina izin verilmektedir. "
            "INSERT, UPDATE, DELETE, DROP, ALTER, EXEC komutlari yasaklanmistir.",
        )

    # TOP limit yoksa ekle
    sql = req.sql.strip()
    sql_upper = sql.upper()
    if "TOP " not in sql_upper[:50]:
        sql = sql_upper.replace("SELECT ", "SELECT TOP 1000 ", 1)
        # Orijinal case'i koru ama TOP ekle
        sql = req.sql.strip()
        idx = sql_upper.find("SELECT") + 6
        sql = sql[:idx] + " TOP 1000" + sql[idx:]

    try:
        start = time.time()
        result = execute_query(sql, database=req.database)
        elapsed = round((time.time() - start) * 1000)

        # datetime nesnelerini serialize et
        for row in result["rows"]:
            for key, val in row.items():
                if hasattr(val, "isoformat"):
                    row[key] = val.isoformat()

        return {
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"],
            "execution_time_ms": elapsed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
