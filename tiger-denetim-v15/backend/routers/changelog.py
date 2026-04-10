from fastapi import APIRouter, HTTPException
from database import execute_query
from queries.sql_queries import CHANGELOG_COMPARISON

router = APIRouter()


@router.get("/changelog")
def get_changelog():
    try:
        rows = {r["tablo"]: r["sayi"] for r in execute_query(CHANGELOG_COMPARISON)["rows"]}
        k320, y320 = rows.get("320_KAYNAK", 0), rows.get("320_YEDEK", 0)
        k321, y321 = rows.get("321_KAYNAK", 0), rows.get("321_YEDEK", 0)
        return {
            "firma_320": {"kaynak": k320, "yedek": y320, "fark": k320 - y320, "ok": k320 >= y320},
            "firma_321": {"kaynak": k321, "yedek": y321, "fark": k321 - y321, "ok": k321 >= y321},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
