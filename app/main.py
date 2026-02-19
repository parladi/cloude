"""
e-Belge Yerel Arşiv Yöneticisi
Streamlit tabanlı, tek kullanıcılı, offline çalışan uygulama.

Çalıştırma:
    streamlit run app/main.py
"""
import os
import sys

# Proje kök dizinini sys.path'e ekle (streamlit run app/main.py şeklinde çalıştırıldığında)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

# ── Sayfa konfigürasyonu (ilk Streamlit çağrısı olmalı) ──────────────────────
st.set_page_config(
    page_title="e-Belge Arşiv",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.db import storage
from app.ui import login as login_ui
from app.ui import indexing, search, errors as errors_ui


# ── CACHE KONUMU ─────────────────────────────────────────────────────────────
# Cache, script'in çalıştığı dizinde oluşturulur (veya önceki root_folder'dan alınır).
# İlk çalıştırmada: ./cache/  (proje dizininde)
# Kullanıcı kök klasör seçince: root_folder/cache/

_DEFAULT_CACHE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
_DB_PATH = os.path.join(_DEFAULT_CACHE, "app.db")

os.makedirs(_DEFAULT_CACHE, exist_ok=True)

# DB başlatma
storage.init_db(_DB_PATH)

# Kaydedilmiş kök klasör varsa cache yolunu güncelle
_saved_root = storage.get_meta(_DB_PATH, "root_folder")
if _saved_root and os.path.isdir(_saved_root):
    _CACHE_DIR = os.path.join(_saved_root, "cache")
    _ALT_DB = os.path.join(_CACHE_DIR, "app.db")
    # Farklı bir DB mi?
    if _ALT_DB != _DB_PATH:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        storage.init_db(_ALT_DB)
        # Auth tablosunu taşı (bir kez)
        if not storage.user_exists(_ALT_DB) and storage.user_exists(_DB_PATH):
            import sqlite3
            src = sqlite3.connect(_DB_PATH)
            dst = sqlite3.connect(_ALT_DB)
            for row in src.execute("SELECT * FROM auth").fetchall():
                try:
                    dst.execute("INSERT OR IGNORE INTO auth VALUES(?,?,?)", row)
                    dst.commit()
                except Exception:
                    pass
            src.close(); dst.close()
        _DB_PATH = _ALT_DB
else:
    _CACHE_DIR = _DEFAULT_CACHE


# ── GİRİŞ KONTROLÜ ───────────────────────────────────────────────────────────
login_ui.show_login(_DB_PATH)


# ── ANA UYGULAMA ─────────────────────────────────────────────────────────────
def main() -> None:
    # Üst çubuk
    header_col, logout_col = st.columns([6, 1])
    with header_col:
        st.title("📦 e-Belge Yerel Arşiv")
    with logout_col:
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Sekme yönetimi — kök klasör değişince DB yolu da güncellensin
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📁 İndeksleme", "🔍 Arama / Filtre", "⚠️ Hatalar", "⚙️ Ayarlar"]
    )

    with tab1:
        _show_indexing_tab()

    with tab2:
        search.show_search(_get_active_db())

    with tab3:
        errors_ui.show_errors(_get_active_db())

    with tab4:
        _show_settings_tab()


def _get_active_db() -> str:
    """Güncel aktif DB yolunu döner."""
    saved_root = storage.get_meta(_DB_PATH, "root_folder")
    if saved_root and os.path.isdir(saved_root):
        candidate = os.path.join(saved_root, "cache", "app.db")
        if os.path.isfile(candidate):
            return candidate
    return _DB_PATH


def _get_active_cache() -> str:
    saved_root = storage.get_meta(_DB_PATH, "root_folder")
    if saved_root and os.path.isdir(saved_root):
        return os.path.join(saved_root, "cache")
    return _CACHE_DIR


def _show_indexing_tab() -> None:
    """İndeksleme sekmesi: kök klasör değişince DB yolunu da güncelle."""
    db = _get_active_db()
    cache = _get_active_cache()
    indexing.show_indexing(db, cache)

    # Kök klasör değişmişse yeni DB oluştur
    new_root = storage.get_meta(db, "root_folder")
    if new_root and os.path.isdir(new_root):
        new_cache = os.path.join(new_root, "cache")
        new_db = os.path.join(new_cache, "app.db")
        if new_db != db:
            os.makedirs(new_cache, exist_ok=True)
            storage.init_db(new_db)
            # root_folder'ı yeni DB'ye de yaz
            storage.set_meta(new_db, "root_folder", new_root)
            # Auth'u taşı
            if not storage.user_exists(new_db) and storage.user_exists(db):
                import sqlite3
                src = sqlite3.connect(db)
                dst = sqlite3.connect(new_db)
                for row in src.execute("SELECT * FROM auth").fetchall():
                    try:
                        dst.execute("INSERT OR IGNORE INTO auth VALUES(?,?,?)", row)
                        dst.commit()
                    except Exception:
                        pass
                src.close(); dst.close()


def _show_settings_tab() -> None:
    from app.ui.login import change_password_widget

    st.header("Ayarlar")

    db = _get_active_db()
    cache = _get_active_cache()

    st.subheader("Veritabanı")
    stats = storage.get_stats(db)
    c1, c2, c3 = st.columns(3)
    c1.metric("Belgeler", stats["belgeler"])
    c2.metric("Kalemler", stats["kalemler"])
    c3.metric("Hatalar", stats["hatalar"])

    col_reset, col_reindex = st.columns(2)
    with col_reset:
        if st.button("Cache Sıfırla (tüm verileri sil)", type="secondary"):
            storage.clear_all(db)
            st.success("Cache temizlendi. İndeksleme sekmesinden yeniden tarayabilirsiniz.")
            st.rerun()

    with col_reindex:
        st.info("Yeniden indekslemek için 'İndeksleme' sekmesini kullanın.")

    st.markdown("---")

    change_password_widget(db)

    st.markdown("---")
    st.subheader("Bilgi")
    st.markdown(f"""
    - **DB Konumu:** `{db}`
    - **Cache Dizini:** `{cache}`
    - **Versiyon:** 1.0.0
    """)


if __name__ == "__main__":
    main()
else:
    # Streamlit dosyayı modül olarak import ederse de main() çalışsın
    main()
