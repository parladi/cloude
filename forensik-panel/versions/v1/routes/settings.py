"""Ayarlar sayfası"""
import logging

from flask import Blueprint, render_template

from config import CONFIG, CONFIG_DIR, DATA_DIR, PROJECT_ROOT, get_databases
from core.archive import _archive_paths, count_queries

logger = logging.getLogger(__name__)
bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/")
def index():
    duckdb_path, parquet_dir = _archive_paths()

    return render_template(
        "settings.html",
        app_info=CONFIG["uygulama"],
        sql_info={
            "host": CONFIG["sql_server"]["host"],
            "port": CONFIG["sql_server"]["port"],
            "default_database": CONFIG["sql_server"]["default_database"],
            "query_timeout": CONFIG["sql_server"].get("query_timeout", 600),
            "user_env": CONFIG["sql_server"]["user_env"],
            "password_env": CONFIG["sql_server"]["password_env"],
        },
        arsiv_info={
            "duckdb_path": str(duckdb_path),
            "parquet_dir": str(parquet_dir),
            "query_count": count_queries(),
            "max_display_rows": CONFIG["arsiv"].get("max_display_rows", 1000),
        },
        paths={
            "project_root": str(PROJECT_ROOT),
            "config_dir": str(CONFIG_DIR),
            "data_dir": str(DATA_DIR),
            "log_path": str(DATA_DIR / "logs" / "app.log"),
        },
        databases=get_databases(),
    )
