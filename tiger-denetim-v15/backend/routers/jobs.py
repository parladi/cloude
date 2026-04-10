from fastapi import APIRouter, HTTPException
from database import execute_query
from queries.sql_queries import JOBS_STATUS

router = APIRouter()


@router.get("/jobs")
def get_jobs():
    try:
        rows = execute_query(JOBS_STATUS, database="msdb")["rows"]
        for row in rows:
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
        return {"jobs": rows, "active": sum(1 for j in rows if j["durum"] == "AKTIF"), "total": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
