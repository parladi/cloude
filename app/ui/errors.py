"""
Hatalar sekmesi: parse edilemeyen veya bozuk dosyaları listeler.
"""
import pandas as pd
import streamlit as st

from app.db import storage


def show_errors(db_path: str) -> None:
    st.header("Hatalar")
    errors = storage.get_errors(db_path)

    if not errors:
        st.success("Hata kaydı bulunamadı.")
        return

    st.warning(f"Toplam {len(errors)} hata kaydı mevcut.")

    df = pd.DataFrame(errors)
    # Gereksiz sutun kaldır
    for col in ["err_id", "file_hash"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df.columns = [c.upper() for c in df.columns]

    st.dataframe(df, use_container_width=True, height=500)

    # CSV indir
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "Hataları CSV İndir",
        data=csv.encode("utf-8-sig"),
        file_name="hatalar.csv",
        mime="text/csv",
    )
