from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import settings, update_settings
from database import execute_query

router = APIRouter()


class ConnectionConfig(BaseModel):
    server: str
    port: int = 1433
    user: str
    password: str = ""
    database: str = "TIGERDB"
    database_backup: str = "VeribanLocalDB"


@router.get("/connection")
def get_connection():
    """Mevcut baglanti ayarlarini dondur"""
    return {
        "server": settings.DB_SERVER,
        "port": settings.DB_PORT,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "database": settings.DB_NAME,
        "database_backup": settings.DB_NAME_BACKUP,
    }


@router.post("/connection/test")
def test_connection(config: ConnectionConfig):
    """Verilen ayarlarla baglanti testi yap"""
    import pymssql

    try:
        conn = pymssql.connect(
            server=config.server,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT @@SERVERNAME AS server_name, @@VERSION AS version")
        row = cursor.fetchone()
        conn.close()
        return {
            "success": True,
            "message": "Baglanti basarili!",
            "server_name": row[0] if row else None,
            "version": row[1][:80] if row and row[1] else None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Baglanti hatasi: {str(e)}",
        }


@router.post("/connection/save")
def save_connection(config: ConnectionConfig):
    """Baglanti ayarlarini kaydet ve uygula"""
    import pymssql

    # Once test et
    try:
        conn = pymssql.connect(
            server=config.server,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Baglanti kurulamadi: {str(e)}")

    # Basarili ise ayarlari guncelle
    update_settings(
        server=config.server,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
        database_backup=config.database_backup,
    )

    return {
        "success": True,
        "message": "Ayarlar kaydedildi ve uygulandı.",
        "server": settings.DB_SERVER,
        "database": settings.DB_NAME,
    }
