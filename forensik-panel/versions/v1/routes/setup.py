"""İlk kurulum — SQL kimliklerini .env'e yazar"""
import logging
import os

from flask import Blueprint, jsonify, render_template, request

from config import CONFIG, get_databases, get_default_database
from core.db import test_connection_with_creds
from core.env_manager import (PLACEHOLDER_VALUES, ENV_PATH, is_configured,
                              read_env, write_env)

logger = logging.getLogger(__name__)
bp = Blueprint("setup", __name__, url_prefix="/setup")


def _defaults() -> dict:
    """Form için varsayılan değerler — .env veya config.yaml'dan"""
    env = read_env()
    user_key = CONFIG["sql_server"]["user_env"]
    pass_key = CONFIG["sql_server"]["password_env"]

    user = env.get(user_key) or os.getenv(user_key) or "sa"
    if user in PLACEHOLDER_VALUES:
        user = "sa"

    host = (env.get("FORENSIK_SQL_HOST") or os.getenv("FORENSIK_SQL_HOST")
            or CONFIG["sql_server"]["host"])
    port_raw = (env.get("FORENSIK_SQL_PORT") or os.getenv("FORENSIK_SQL_PORT")
                or CONFIG["sql_server"]["port"])
    try:
        port = int(port_raw)
    except (ValueError, TypeError):
        port = 1433

    return {
        "host": host,
        "port": port,
        "user": user,
        "database": get_default_database(),
    }


@bp.route("/", methods=["GET"])
def index():
    return render_template(
        "setup.html",
        defaults=_defaults(),
        databases=get_databases(),
    )


def _read_payload() -> dict:
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()
    return {
        "host": (data.get("host") or "").strip(),
        "port": (str(data.get("port") or "1433")).strip(),
        "user": (data.get("user") or "").strip(),
        "password": data.get("password") or "",
        "database": (data.get("database") or "").strip() or get_default_database(),
    }


@bp.route("/test", methods=["POST"])
def test():
    p = _read_payload()
    if not p["user"] or not p["password"]:
        return jsonify({"status": "error", "error": "Kullanici ve sifre zorunlu"}), 400
    try:
        port = int(p["port"])
    except ValueError:
        return jsonify({"status": "error", "error": "Port gecersiz"}), 400

    result = test_connection_with_creds(
        host=p["host"], port=port, user=p["user"],
        password=p["password"], database=p["database"], timeout=10,
    )
    return jsonify(result)


@bp.route("/save", methods=["POST"])
def save():
    p = _read_payload()
    if not p["user"] or not p["password"]:
        return jsonify({"status": "error", "error": "Kullanici ve sifre zorunlu"}), 400
    try:
        port = int(p["port"])
    except ValueError:
        return jsonify({"status": "error", "error": "Port gecersiz"}), 400

    # Önce test
    result = test_connection_with_creds(
        host=p["host"], port=port, user=p["user"],
        password=p["password"], database=p["database"], timeout=10,
    )
    if result.get("status") != "ok":
        return jsonify(result), 400

    # Sonra .env'e yaz
    user_key = CONFIG["sql_server"]["user_env"]
    pass_key = CONFIG["sql_server"]["password_env"]

    updates = {
        user_key: p["user"],
        pass_key: p["password"],
        "FORENSIK_SQL_HOST": p["host"],
        "FORENSIK_SQL_PORT": str(port),
    }

    # FLASK_SECRET yoksa rastgele üret
    env = read_env()
    if not env.get("FLASK_SECRET") and not os.getenv("FLASK_SECRET"):
        import secrets
        updates["FLASK_SECRET"] = secrets.token_urlsafe(32)

    try:
        write_env(updates)
    except Exception as e:
        logger.exception(".env yazilamadi")
        return jsonify({"status": "error", "error": f".env yazilamadi: {e}"}), 500

    logger.info(f"Kurulum tamamlandi: user={p['user']}, host={p['host']}:{port}")
    return jsonify({"status": "ok", "message": "Kaydedildi", "env_path": str(ENV_PATH)})
