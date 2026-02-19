"""
ZIP ve XML dosyalarını recursive olarak tarar.
yields: (file_path: str, xml_bytes: bytes, zip_hash: str | None)
"""
import os
import zipfile
from typing import Generator, Tuple, Optional

from app.utils.hashing import sha1_bytes, sha1_file


def iterate_xml_files(
    root_folder: str,
) -> Generator[Tuple[str, bytes, str], None, None]:
    """
    Kök klasörü ve alt klasörlerini recursive tarar.
    ZIP içindeki ve doğrudan klasördeki XML'leri yield eder.
    Yield: (kaynak_yol, xml_bytes, dosya_hash)
      - kaynak_yol: ZIP ise  'zip_path::entry_name', değilse dosya_yolu
    """
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # cache klasörünü atla
        dirnames[:] = [d for d in dirnames if d != "cache"]

        for fname in filenames:
            full_path = os.path.join(dirpath, fname)

            if fname.lower().endswith(".zip"):
                # ZIP içindeki XML'leri oku
                try:
                    zip_hash = sha1_file(full_path)
                    with zipfile.ZipFile(full_path, "r") as zf:
                        for entry in zf.namelist():
                            if entry.lower().endswith(".xml"):
                                try:
                                    xml_bytes = zf.read(entry)
                                    entry_hash = sha1_bytes(xml_bytes)
                                    source = f"{full_path}::{entry}"
                                    yield source, xml_bytes, entry_hash
                                except Exception:
                                    # bozuk entry → çağıran handle edecek
                                    yield f"{full_path}::{entry}", b"", "__READ_ERROR__"
                except zipfile.BadZipFile:
                    yield full_path, b"", "__BAD_ZIP__"
                except Exception:
                    yield full_path, b"", "__ZIP_ERROR__"

            elif fname.lower().endswith(".xml"):
                # Doğrudan XML dosyası
                try:
                    with open(full_path, "rb") as f:
                        xml_bytes = f.read()
                    file_hash = sha1_bytes(xml_bytes)
                    yield full_path, xml_bytes, file_hash
                except Exception:
                    yield full_path, b"", "__READ_ERROR__"
