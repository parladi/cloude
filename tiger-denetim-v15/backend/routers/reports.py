from fastapi import APIRouter, HTTPException
from database import execute_query
from queries.sql_queries import COMPUTER_DISTRIBUTION, DAILY_TREND

router = APIRouter()


def serialize_rows(rows):
    for row in rows:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    return rows


@router.get("/reports/risk-computers")
def risk_computers():
    try:
        return {"computers": serialize_rows(execute_query(COMPUTER_DISTRIBUTION)["rows"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/timeline")
def timeline():
    try:
        r = execute_query(DAILY_TREND)
        return {"columns": r["columns"], "rows": serialize_rows(r["rows"]), "row_count": r["row_count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
