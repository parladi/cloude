"""
Indeksleme sekmesi:
- Kok klasor secimi
- Alt klasor agaci ve ZIP dosya listesi
- Taramayi baslat / durdur
- Ilerleme cubugu
- Artimli indeksleme (hash kontrolu)
"""
import os
import zipfile

import streamlit as st

from app.db import storage
from app.parsing import pdf_extract, ubl_parser
from app.utils.zip_reader import iterate_xml_files


def show_indexing(db_path: str, cache_dir: str) -> None:
    st.header("Indeksleme")

    # Kok klasor girisi
    default_root = storage.get_meta(db_path, "root_folder") or ""
    root_folder = st.text_input(
        "Kok Klasor Yolu",
        value=default_root,
        placeholder=r"Orn: C:\Belgeler\eArsiv veya /home/user/belgeler",
        help="Icinde ay klasorlerinin (1, 2, 3 ...) bulundugu ana klasor.",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        start_btn = st.button("Taramayi Baslat", type="primary", use_container_width=True)
    with col2:
        reset_btn = st.button("Cache Sifirla", use_container_width=True)

    # Klasor agaci ve ZIP dosya listesi
    root_folder_stripped = root_folder.strip()
    if root_folder_stripped and os.path.isdir(root_folder_stripped):
        _show_folder_browser(root_folder_stripped)

    # Istatistikler
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

    # Klasor dogrulama
    if not root_folder_stripped:
        st.error("Lutfen kok klasor yolunu girin.")
        return
    if not os.path.isdir(root_folder_stripped):
        st.error(f"Klasor bulunamadi: {root_folder_stripped}")
        return

    # Kok klasoru meta'ya kaydet
    storage.set_meta(db_path, "root_folder", root_folder_stripped)

    # Tarama basliyor
    status_box = st.empty()
    progress_bar = st.progress(0)
    log_box = st.empty()
    logs: list[str] = []

    def add_log(msg: str) -> None:
        logs.append(msg)
        # Son 15 log goster
        log_box.text_area("Log", "\n".join(logs[-15:]), height=220, key=f"log_{len(logs)}")

    status_box.info("Dosyalar taraniyor...")
    add_log(f"Kok klasor: {root_folder_stripped}")

    processed = 0
    skipped = 0
    inserted = 0
    errors = 0

    # Tum XML dosyalarini listele
    for source_path, xml_bytes, file_hash in iterate_xml_files(root_folder_stripped):
        processed += 1

        # Ozel hata durumlari
        if file_hash in ("__BAD_ZIP__", "__ZIP_ERROR__", "__READ_ERROR__"):
            err_msg = {
                "__BAD_ZIP__": "Bozuk ZIP dosyasi",
                "__ZIP_ERROR__": "ZIP acma hatasi",
                "__READ_ERROR__": "Dosya okuma hatasi",
            }.get(file_hash, "Bilinmeyen hata")
            storage.log_error(db_path, source_path, file_hash, err_msg)
            add_log(f"[HATA] {source_path}: {err_msg}")
            errors += 1
            status_box.warning(f"Isleniyor... {processed} dosya, {errors} hata")
            continue

        # Artimli indeksleme: ayni hash var mi?
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
                    add_log(f"[UYARI] PDF kayit hatasi: {e}")

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
                storage.log_error(db_path, source_path, file_hash, f"DB yazma hatasi: {e}")
                add_log(f"[HATA] DB: {e}")
                errors += 1

        if processed % 10 == 0:
            status_box.info(f"Isleniyor... {processed} dosya, {inserted} yeni, {skipped} atlandi, {errors} hata")

    progress_bar.progress(1.0)
    status_box.success(
        f"Tarama tamamlandi: {processed} dosya islendi, "
        f"{inserted} belge eklendi, {skipped} atlandi, {errors} hata."
    )

    # Istatistikleri yenile
    stats = storage.get_stats(db_path)
    m1.metric("Belgeler", stats["belgeler"])
    m2.metric("Kalemler", stats["kalemler"])
    m3.metric("Hatalar", stats["hatalar"])


def _show_folder_browser(root_folder: str) -> None:
    """Kok klasorun alt klasorlerini ve ZIP/XML dosyalarini listeler."""
    with st.expander("Klasor Icerigi", expanded=False):
        folder_info = _scan_folder_summary(root_folder)

        # Ozet bilgi
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Alt Klasor", folder_info["dir_count"])
        sc2.metric("ZIP Dosya", folder_info["zip_count"])
        sc3.metric("XML Dosya", folder_info["xml_count"])

        if folder_info["items"]:
            for item in folder_info["items"]:
                icon = item["icon"]
                name = item["name"]
                detail = item["detail"]
                st.markdown(f"`{icon}` **{name}** {detail}")
        else:
            st.info("Klasor bos veya erisim izni yok.")


def _scan_folder_summary(root_folder: str, max_depth: int = 2) -> dict:
    """Klasor icerigin ozetini cikarir (max_depth seviyeye kadar)."""
    items = []
    dir_count = 0
    zip_count = 0
    xml_count = 0

    try:
        entries = sorted(os.listdir(root_folder))
    except PermissionError:
        return {"items": [], "dir_count": 0, "zip_count": 0, "xml_count": 0}

    for entry in entries:
        full = os.path.join(root_folder, entry)
        if entry == "cache":
            continue

        if os.path.isdir(full):
            dir_count += 1
            # Alt klasordeki dosya sayilarini say
            sub_zips = 0
            sub_xmls = 0
            try:
                for sub_entry in os.listdir(full):
                    sl = sub_entry.lower()
                    if sl.endswith(".zip"):
                        sub_zips += 1
                    elif sl.endswith(".xml"):
                        sub_xmls += 1
            except PermissionError:
                pass
            detail = ""
            parts = []
            if sub_zips:
                parts.append(f"{sub_zips} ZIP")
            if sub_xmls:
                parts.append(f"{sub_xmls} XML")
            if parts:
                detail = f"— {', '.join(parts)}"
            items.append({"icon": "📁", "name": entry, "detail": detail})

        elif entry.lower().endswith(".zip"):
            zip_count += 1
            # ZIP icerigini kontrol et
            xml_in_zip = 0
            try:
                with zipfile.ZipFile(full, "r") as zf:
                    xml_in_zip = sum(1 for n in zf.namelist() if n.lower().endswith(".xml"))
            except Exception:
                pass
            detail = f"— {xml_in_zip} XML iceriyor" if xml_in_zip else "— bos veya bozuk"
            items.append({"icon": "📦", "name": entry, "detail": detail})

        elif entry.lower().endswith(".xml"):
            xml_count += 1
            size_kb = os.path.getsize(full) / 1024
            items.append({"icon": "📄", "name": entry, "detail": f"— {size_kb:.0f} KB"})

    return {
        "items": items[:50],  # Cok fazla gosterme
        "dir_count": dir_count,
        "zip_count": zip_count,
        "xml_count": xml_count,
    }
