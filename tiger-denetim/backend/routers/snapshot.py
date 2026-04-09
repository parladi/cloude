from fastapi import APIRouter, HTTPException

from database import execute_query
from queries.sql_queries import SNAPSHOT_COMPARISON

router = APIRouter()


@router.get("/snapshot")
def get_snapshot():
    """19 tablo snapshot vs guncel karsilastirma"""
    try:
        result = execute_query(SNAPSHOT_COMPARISON)
        rows = result["rows"]

        for row in rows:
            snapshot = row.get("snapshot_kayit") or 0
            guncel = row.get("guncel_kayit") or 0
            row["fark"] = guncel - snapshot
            if guncel < snapshot:
                row["durum"] = "ALARM"
            elif guncel == snapshot:
                row["durum"] = "OK"
            else:
                row["durum"] = "NORMAL"

        return {"tables": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
