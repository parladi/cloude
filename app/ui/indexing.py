"""
İndeksleme sekmesi:
- Kök klasör seçimi
- Taramayı başlat / durdur
- İlerleme çubuğu
- Artımlı indeksleme (hash kontrolü)
"""
import os
import streamlit as st

from app.db import storage
from app.parsing import pdf_extract, ubl_parser
from app.utils.zip_reader import iterate_xml_files


def show_indexing(db_path: str, cache_dir: str) -> None:
    st.header("İndeksleme")

    # Kök klasör girişi
    default_root = storage.get_meta(db_path, "root_folder") or ""
    root_folder = st.text_input(
        "Kök Klasör Yolu",
        value=default_root,
        placeholder=r"Örn: C:\Belgeler\eArsiv veya /home/user/belgeler",
        help="İçinde ay klasörlerinin (1, 2, 3 ...) bulunduğu ana klasör.",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        start_btn = st.button("Taramayı Başlat", type="primary", use_container_width=True)
    with col2:
        reset_btn = st.button("Cache Sıfırla", use_container_width=True)

    # İstatistikler
    stats = storage.get_stats(db_path)
    m1, m2, m3 = st.columns(3)
    m1.metric("Belgeler", stats["belgeler"])
    m2.metric("Kalemler", stats["kalemler"])
    m3.metric("Hatalar", stats["hatalar"])

    if reset_btn:
        storage.clear_all(db_path)
        st.success("Cache temizlendi.")
        st.rerun()

    if not start_btn:
        return

    # Klasör doğrulama
    root_folder = root_folder.strip()
    if not root_folder:
        st.error("Lütfen kök klasör yolunu girin.")
        return
    if not os.path.isdir(root_folder):
        st.error(f"Klasör bulunamadı: {root_folder}")
        return

    # Kök klasörü meta'ya kaydet
    storage.set_meta(db_path, "root_folder", root_folder)

    # Tarama başlıyor
    status_box = st.empty()
    progress_bar = st.progress(0)
    log_box = st.empty()
    logs: list[str] = []

    def add_log(msg: str) -> None:
        logs.append(msg)
        # Son 15 log göster
        log_box.text_area("Log", "\n".join(logs[-15:]), height=220, key=f"log_{len(logs)}")

    status_box.info("Dosyalar taranıyor...")
    add_log(f"Kök klasör: {root_folder}")

    processed = 0
    skipped = 0
    inserted = 0
    errors = 0

    # Tüm XML dosyalarını listele (ilerleme için ön sayım gerekmiyor; streaming yapıyoruz)
    for source_path, xml_bytes, file_hash in iterate_xml_files(root_folder):
        processed += 1

        # Özel hata durumları
        if file_hash in ("__BAD_ZIP__", "__ZIP_ERROR__", "__READ_ERROR__"):
            err_msg = {
                "__BAD_ZIP__": "Bozuk ZIP dosyası",
                "__ZIP_ERROR__": "ZIP açma hatası",
                "__READ_ERROR__": "Dosya okuma hatası",
            }.get(file_hash, "Bilinmeyen hata")
            storage.log_error(db_path, source_path, file_hash, err_msg)
            add_log(f"[HATA] {source_path}: {err_msg}")
            errors += 1
            status_box.warning(f"İşleniyor... {processed} dosya, {errors} hata")
            continue

        # Artımlı indeksleme: aynı hash var mı?
        if storage.hash_exists(db_path, file_hash):
            skipped += 1
            continue

        # Parse
        doc, lines, pdf_bytes, err = ubl_parser.parse_xml(xml_bytes, source_path, file_hash)

        if err:
            storage.log_error(db_path, source_path, file_hash, err)
            add_log(f"[HATA] {os.path.basename(source_path.split('::')[-1])}: {err}")
            errors += 1
        else:
            # PDF kaydet
            if pdf_bytes and doc:
                try:
                    pdf_path = pdf_extract.save_pdf(pdf_bytes, cache_dir, doc["doc_id"])
                    doc["embedded_pdf_path"] = pdf_path
                except Exception as e:
                    add_log(f"[UYARI] PDF kayıt hatası: {e}")

            # DB'ye yaz
            try:
                storage.insert_doc(db_path, doc)
                if lines:
                    storage.insert_lines(db_path, lines)
                inserted += 1
                add_log(
                    f"[OK] {doc.get('doc_type','?')} | {doc.get('doc_no','?')} "
                    f"| {len(lines)} kalem"
                )
            except Exception as e:
                storage.log_error(db_path, source_path, file_hash, f"DB yazma hatası: {e}")
                add_log(f"[HATA] DB: {e}")
                errors += 1

        if processed % 10 == 0:
            status_box.info(f"İşleniyor... {processed} dosya, {inserted} yeni, {skipped} atlandı, {errors} hata")

    progress_bar.progress(1.0)
    status_box.success(
        f"Tarama tamamlandı: {processed} dosya işlendi, "
        f"{inserted} belge eklendi, {skipped} atlandı, {errors} hata."
    )

    # İstatistikleri yenile
    stats = storage.get_stats(db_path)
    m1.metric("Belgeler", stats["belgeler"])
    m2.metric("Kalemler", stats["kalemler"])
    m3.metric("Hatalar", stats["hatalar"])
