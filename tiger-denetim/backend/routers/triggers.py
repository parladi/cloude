from fastapi import APIRouter, HTTPException

from database import execute_query
from queries.sql_queries import TRIGGERS_STATUS

router = APIRouter()


@router.get("/triggers")
def get_triggers():
    """18 trigger'in durumu"""
    try:
        result = execute_query(TRIGGERS_STATUS)
        rows = result["rows"]
        # datetime nesnelerini string'e cevir
        for row in rows:
            for key in ("olusturma_tarihi", "son_degisiklik"):
                if row.get(key) and hasattr(row[key], "isoformat"):
                    row[key] = row[key].isoformat()
        return {
            "triggers": rows,
            "active": sum(1 for t in rows if t["durum"] == "AKTIF"),
            "total": len(rows),
            "disabled": [t["trigger_adi"] for t in rows if t["durum"] == "KAPALI"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
