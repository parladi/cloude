import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import execute_query

router = APIRouter()

FORBIDDEN = ['INSERT','UPDATE','DELETE','DROP','ALTER','EXEC','EXECUTE','xp_','sp_','TRUNCATE','CREATE','GRANT','REVOKE']


class QueryRequest(BaseModel):
    sql: str
    database: str = "TIGERDB"


@router.post("/query")
def run_query(req: QueryRequest):
    sql_upper = req.sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Sadece SELECT sorgularina izin verilmektedir.")
    for kw in FORBIDDEN:
        if kw.upper() in sql_upper:
            raise HTTPException(status_code=400, detail=f"'{kw}' komutu yasaklanmistir.")
    sql = req.sql.strip()
    if "TOP " not in sql.upper()[:50]:
        idx = sql.upper().find("SELECT") + 6
        sql = sql[:idx] + " TOP 1000" + sql[idx:]
    try:
        start = time.time()
        r = execute_query(sql, database=req.database)
        elapsed = round((time.time() - start) * 1000)
        for row in r["rows"]:
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
        return {"columns": r["columns"], "rows": r["rows"], "row_count": r["row_count"], "execution_time_ms": elapsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
