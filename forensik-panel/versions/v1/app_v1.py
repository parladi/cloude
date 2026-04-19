"""Forensik Panel — Flask giriş noktası"""
import logging
import os
import threading
import time
import webbrowser
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

from config import CONFIG, get_default_database
from core.env_manager import is_configured
from core.logging_setup import setup_logging


def create_app() -> Flask:
    setup_logging()
    logger = logging.getLogger(__name__)

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "dev-secret-change-me")
    app.config["FORENSIK_VERSION"] = CONFIG["uygulama"]["surum"]

    from routes.dashboard import bp as dashboard_bp
    from routes.databases import bp as databases_bp
    from routes.sql_editor import bp as sql_editor_bp
    from routes.archive import bp as archive_bp
    from routes.diff import bp as diff_bp
    from routes.settings import bp as settings_bp
    from routes.debug import bp as debug_bp
    from routes.setup import bp as setup_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(databases_bp)
    app.register_blueprint(sql_editor_bp)
    app.register_blueprint(archive_bp)
    app.register_blueprint(diff_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(setup_bp)

    # Kimlik yoksa /setup'a yönlendir
    SETUP_FREE_PATHS = ("/setup", "/static/", "/debug/log")

    @app.before_request
    def _ensure_configured():
        path = request.path or "/"
        if any(path == p or path.startswith(p) for p in SETUP_FREE_PATHS):
            return None
        if not is_configured():
            return redirect(url_for("setup.index"))
        return None

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Sunucu hatası")
        return render_template("errors/500.html"), 500

    @app.context_processor
    def inject_globals():
        return {
            "app_version": CONFIG["uygulama"]["surum"],
            "app_name": CONFIG["uygulama"]["isim"],
            "default_database": get_default_database(),
            "now_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    logger.info(f"Flask app oluşturuldu — sürüm {CONFIG['uygulama']['surum']}")
    return app


def open_browser_later(url: str, delay: float = 2.0):
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()


def main():
    app = create_app()
    port = CONFIG["uygulama"]["port"]
    url = f"http://127.0.0.1:{port}"

    print("=" * 60)
    print(f"  FORENSİK PANEL v{CONFIG['uygulama']['surum']}")
    print("=" * 60)
    print(f"  URL:  {url}")
    print(f"  Kapatmak için: Ctrl+C")
    print("=" * 60)

    if os.getenv("FORENSIK_NO_BROWSER") != "1":
        open_browser_later(url, delay=2.0)

    from waitress import serve
    serve(
        app,
        host="127.0.0.1",
        port=port,
        threads=8,
        channel_timeout=900,
        cleanup_interval=60,
        connection_limit=200,
    )


if __name__ == "__main__":
    main()
