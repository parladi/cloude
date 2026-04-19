"""SQL kimlik bilgileri için .env yöneticisi"""
import logging
import os
import re
from pathlib import Path

from config import CONFIG, CONFIG_DIR

logger = logging.getLogger(__name__)

ENV_PATH = CONFIG_DIR / ".env"

# Yedek/placeholder değer
PLACEHOLDER_VALUES = {"", "DEGISTIR_BURADA", "CHANGE_ME", "your-password"}


def _user_env_key() -> str:
    return CONFIG["sql_server"]["user_env"]


def _pass_env_key() -> str:
    return CONFIG["sql_server"]["password_env"]


def is_configured() -> bool:
    """SQL kimlik bilgileri ayarlanmış mı?"""
    user = os.getenv(_user_env_key()) or ""
    password = os.getenv(_pass_env_key()) or ""
    return (
        user.strip() not in PLACEHOLDER_VALUES
        and password.strip() not in PLACEHOLDER_VALUES
    )


def read_env() -> dict:
    """.env içeriğini sözlük olarak oku"""
    out: dict[str, str] = {}
    if not ENV_PATH.exists():
        return out

    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        # tırnak ayıkla
        v = v.strip().strip('"').strip("'")
        out[k.strip()] = v
    return out


def _quote_if_needed(v: str) -> str:
    if not v:
        return ""
    # Boşluk veya özel karakter varsa tırnak içine al
    if re.search(r"[\s#'\"]", v):
        escaped = v.replace('"', '\\"')
        return f'"{escaped}"'
    return v


def write_env(updates: dict[str, str]) -> None:
    """Mevcut .env'yi koruyarak verilen anahtarları güncelle/ekle"""
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing_lines: list[str] = []
    if ENV_PATH.exists():
        existing_lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    seen: set[str] = set()
    new_lines: list[str] = []

    for raw in existing_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(raw)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in updates:
            new_lines.append(f"{key}={_quote_if_needed(updates[key])}")
            seen.add(key)
        else:
            new_lines.append(raw)

    # Yeni anahtarları ekle
    for k, v in updates.items():
        if k not in seen:
            new_lines.append(f"{k}={_quote_if_needed(v)}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    # Süreç içi env'i de güncelle (yeniden başlatmadan kullanılsın)
    for k, v in updates.items():
        os.environ[k] = v

    logger.info(f".env güncellendi: {list(updates.keys())}")
