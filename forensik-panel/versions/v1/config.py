"""Config yükleyici — config.yaml + .env okur"""
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(CONFIG_DIR / ".env")

_config_path = CONFIG_DIR / "config.yaml"
if not _config_path.exists():
    raise FileNotFoundError(f"config.yaml bulunamadi: {_config_path}")

with open(_config_path, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def get_sql_creds():
    user = os.getenv(CONFIG["sql_server"]["user_env"])
    password = os.getenv(CONFIG["sql_server"]["password_env"])
    if not user or not password:
        raise RuntimeError(
            "SQL kimlik bilgisi yok. config/.env dosyasini olusturun."
        )
    return user, password


def get_databases():
    return CONFIG["sql_server"]["databases"]


def get_default_database():
    for db in CONFIG["sql_server"]["databases"]:
        if db.get("varsayilan"):
            return db["name"]
    return CONFIG["sql_server"]["default_database"]
