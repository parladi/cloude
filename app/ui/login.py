"""
Giriş ve ilk kurulum ekranı.
İlk çalıştırmada admin kullanıcısı oluşturma,
sonraki çalıştırmalarda şifre doğrulama.
"""
import bcrypt
import streamlit as st

from app.db import storage


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_pw(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def show_login(db_path: str) -> bool:
    """
    Login UI'ını gösterir.
    Oturum açıksa True döner, değilse False döner ve durur.
    """
    # Zaten giriş yapıldıysa geç
    if st.session_state.get("authenticated"):
        return True

    st.set_page_config(page_title="Giriş", page_icon="🔐", layout="centered")

    # İlk kez kurulum mu?
    if not storage.user_exists(db_path):
        _show_setup(db_path)
    else:
        _show_login_form(db_path)

    st.stop()


def _show_setup(db_path: str) -> None:
    """İlk kurulum - admin kullanıcısı oluştur."""
    st.title("İlk Kurulum")
    st.info("Uygulama ilk kez başlatılıyor. Bir yönetici şifresi belirleyin.")

    with st.form("setup_form"):
        st.text_input("Kullanıcı Adı", value="admin", disabled=True)
        pw1 = st.text_input("Şifre", type="password", key="setup_pw1")
        pw2 = st.text_input("Şifre Tekrar", type="password", key="setup_pw2")
        submitted = st.form_submit_button("Oluştur", type="primary", use_container_width=True)

    if submitted:
        if len(pw1) < 6:
            st.error("Şifre en az 6 karakter olmalı.")
        elif pw1 != pw2:
            st.error("Şifreler eşleşmiyor.")
        else:
            storage.create_user(db_path, "admin", _hash_pw(pw1))
            st.success("Admin kullanıcısı oluşturuldu. Giriş yapın.")
            st.rerun()


def _show_login_form(db_path: str) -> None:
    """Normal login ekranı."""
    st.title("Giriş Yap")

    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı", key="login_user")
        password = st.text_input("Şifre", type="password", key="login_pw")
        submitted = st.form_submit_button("Giriş", type="primary", use_container_width=True)

    if submitted:
        user = storage.get_user(db_path, username)
        if user and _verify_pw(password, user["password_hash"]):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı.")


def change_password_widget(db_path: str) -> None:
    """Ayarlar sekmesinde şifre değiştirme formu."""
    st.subheader("Şifre Değiştir")
    with st.form("change_pw_form"):
        old_pw = st.text_input("Mevcut Şifre", type="password")
        new_pw1 = st.text_input("Yeni Şifre", type="password")
        new_pw2 = st.text_input("Yeni Şifre Tekrar", type="password")
        submitted = st.form_submit_button("Değiştir", type="primary")

    if submitted:
        username = st.session_state.get("username", "admin")
        user = storage.get_user(db_path, username)
        if not user or not _verify_pw(old_pw, user["password_hash"]):
            st.error("Mevcut şifre hatalı.")
        elif len(new_pw1) < 6:
            st.error("Yeni şifre en az 6 karakter olmalı.")
        elif new_pw1 != new_pw2:
            st.error("Yeni şifreler eşleşmiyor.")
        else:
            storage.update_password(db_path, username, _hash_pw(new_pw1))
            st.success("Şifre başarıyla değiştirildi.")
