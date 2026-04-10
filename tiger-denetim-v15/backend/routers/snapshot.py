from fastapi import APIRouter, HTTPException
from database import execute_query
from queries.sql_queries import SNAPSHOT_COMPARISON

router = APIRouter()


@router.get("/snapshot")
def get_snapshot():
    try:
        rows = execute_query(SNAPSHOT_COMPARISON)["rows"]
        for row in rows:
            s, g = row.get("snapshot_kayit") or 0, row.get("guncel_kayit") or 0
            row["fark"] = g - s
            row["durum"] = "ALARM" if g < s else ("OK" if g == s else "NORMAL")
        return {"tables": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
