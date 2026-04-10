from datetime import datetime
from fastapi import APIRouter, HTTPException
from config import settings
from database import execute_query
from queries.sql_queries import DELETION_COUNTS, TRIGGERS_STATUS

router = APIRouter()


@router.get("/health")
def health():
    try:
        execute_query("SELECT 1 AS ok")
        return {"status": "ok", "connected": True, "timestamp": datetime.now().isoformat(), "server": settings.DB_SERVER, "port": settings.DB_PORT, "database": settings.DB_NAME, "database_backup": settings.DB_NAME_BACKUP}
    except Exception as e:
        return {"status": "error", "connected": False, "timestamp": datetime.now().isoformat(), "error": str(e)}


@router.get("/summary")
def summary():
    try:
        tr = execute_query(TRIGGERS_STATUS)
        active = sum(1 for t in tr["rows"] if t["durum"] == "AKTIF")
        disabled = [t["trigger_adi"] for t in tr["rows"] if t["durum"] == "KAPALI"]
        dl = execute_query(DELETION_COUNTS)
        total_del = sum(r["sayi"] for r in dl["rows"])
        cl = {"firm320_ok": None, "firm321_ok": None}
        try:
            from queries.sql_queries import CHANGELOG_COMPARISON
            cr = execute_query(CHANGELOG_COMPARISON)
            d = {r["tablo"]: r["sayi"] for r in cr["rows"]}
            cl["firm320_ok"] = d.get("320_KAYNAK", 0) >= d.get("320_YEDEK", 0)
            cl["firm321_ok"] = d.get("321_KAYNAK", 0) >= d.get("321_YEDEK", 0)
        except Exception:
            pass
        jd = {"active": 0, "total": 0, "last_run": None}
        try:
            from queries.sql_queries import JOBS_STATUS
            jr = execute_query(JOBS_STATUS, database="msdb")
            jd["total"] = len(jr["rows"])
            jd["active"] = sum(1 for j in jr["rows"] if j["durum"] == "AKTIF")
        except Exception:
            pass
        return {"connected": True, "timestamp": datetime.now().isoformat(), "triggers": {"active": active, "total": len(tr["rows"]), "disabled": disabled}, "deletions": {"total": total_del, "by_table": [{"kategori": r["kategori"], "sayi": r["sayi"]} for r in dl["rows"]]}, "changelog": cl, "jobs": jd}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
