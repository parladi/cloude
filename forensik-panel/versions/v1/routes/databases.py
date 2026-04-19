"""Veritabanları listesi ve bağlantı testi"""
import logging

from flask import Blueprint, jsonify, render_template, request

from config import get_databases
from core.db import test_connection

logger = logging.getLogger(__name__)
bp = Blueprint("databases", __name__, url_prefix="/databases")


@bp.route("/")
def index():
    return render_template("databases.html", databases=get_databases())


@bp.route("/test")
def test():
    db = (request.args.get("database") or "").strip()
    if not db:
        return jsonify({"status": "error", "error": "database parametresi yok"}), 400
    result = test_connection(db)
    return jsonify(result)
