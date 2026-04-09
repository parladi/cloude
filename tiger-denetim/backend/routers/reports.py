from fastapi import APIRouter, HTTPException

from database import execute_query
from queries.sql_queries import COMPUTER_DISTRIBUTION, DAILY_TREND

router = APIRouter()


def serialize_rows(rows):
    for row in rows:
        for key, val in row.items():
            if hasattr(val, "isoformat"):
                row[key] = val.isoformat()
    return rows


@router.get("/reports/risk-computers")
def risk_computers():
    """Bilgisayar risk skorlari"""
    try:
        result = execute_query(COMPUTER_DISTRIBUTION)
        return {"computers": serialize_rows(result["rows"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/timeline")
def timeline():
    """Gunluk silme trendi"""
    try:
        result = execute_query(DAILY_TREND)
        return {
            "columns": result["columns"],
            "rows": serialize_rows(result["rows"]),
            "row_count": result["row_count"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
