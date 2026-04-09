from fastapi import APIRouter, HTTPException

from database import execute_query
from queries.sql_queries import JOBS_STATUS

router = APIRouter()


@router.get("/jobs")
def get_jobs():
    """SQL Agent job durumlari"""
    try:
        result = execute_query(JOBS_STATUS, database="msdb")
        rows = result["rows"]
        for row in rows:
            for key, val in row.items():
                if hasattr(val, "isoformat"):
                    row[key] = val.isoformat()
        return {
            "jobs": rows,
            "active": sum(1 for j in rows if j["durum"] == "AKTIF"),
            "total": len(rows),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
