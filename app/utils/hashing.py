"""SHA-1 hash yardımcısı - artımlı indeksleme için."""
import hashlib


def sha1_bytes(data: bytes) -> str:
    """Byte verisinin SHA-1 hash'ini döner."""
    return hashlib.sha1(data).hexdigest()


def sha1_file(file_path: str) -> str:
    """Dosyanın SHA-1 hash'ini döner."""
    h = hashlib.sha1()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
