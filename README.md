# e-Belge Yerel Arşiv Yöneticisi

Tarayıcı tabanlı (Streamlit), yerel ve offline çalışan e-İrsaliye / e-Fatura görüntüleyici ve arama aracı.

## Özellikler

- Kök klasörü ve alt klasörleri (ay klasörleri) otomatik tarar
- ZIP ve XML dosyalarını okur, UBL TR1.2 belgelerini parse eder
- e-İrsaliye (DespatchAdvice) ve e-Fatura (Invoice) destekli
- Artımlı indeksleme: aynı dosya ikinci kez işlenmez (SHA-1 hash)
- SQLite ile hızlı arama ve filtreleme
- Gömülü PDF varsa PDF önizleme, yoksa HTML önizleme
- CSV ve Excel (XLSX) export
- Şifreli kullanıcı girişi (bcrypt)

---

## Kurulum

### Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

> **Not:** Python 3.11 veya üzeri gereklidir.

---

## İlk Kullanım

1. Uygulama ilk açıldığında **kurulum ekranı** gösterilir.
2. Admin şifresi belirleyin (en az 6 karakter).
3. Giriş yaptıktan sonra **İndeksleme** sekmesine gidin.
4. Kök klasör yolunu girin (örn. `C:\eArsiv` veya `/home/user/eArsiv`).
   - Bu klasörün altında `1`, `2`, `3` gibi ay alt klasörleri olmalı.
   - Alt klasörlerde ZIP ve/veya XML dosyaları bulunmalı.
5. **Taramayı Başlat** butonuna tıklayın.
6. Tarama tamamlanınca **Arama / Filtre** sekmesine geçin.

---

## Klasör Yapısı (Örnek)

```
eArsiv/               ← Kök klasör
├── 1/                ← Ocak
│   ├── faturalar.zip
│   └── irsaliye.xml
├── 2/                ← Şubat
│   └── belgeler.zip
└── cache/            ← Otomatik oluşturulur
    ├── app.db
    └── pdfs/
```

---

## Proje Yapısı

```
app/
├── main.py                  # Streamlit giriş noktası
├── db/
│   └── storage.py           # SQLite işlemleri
├── parsing/
│   ├── ubl_parser.py        # XML parse (DespatchAdvice + Invoice)
│   ├── pdf_extract.py       # Gömülü PDF kaydetme
│   └── html_render.py       # HTML önizleme şablonu
├── utils/
│   ├── hashing.py           # SHA-1 hash
│   └── zip_reader.py        # ZIP/XML tarayıcı
└── ui/
    ├── login.py             # Giriş ekranı
    ├── indexing.py          # İndeksleme sekmesi
    ├── search.py            # Arama/Filtre sekmesi
    ├── preview.py           # Belge önizleme
    └── errors.py            # Hata listesi sekmesi
```

---

## SQLite Cache Konumu

Seçilen kök klasörün altında `cache/app.db` olarak oluşturulur.
Kök klasör seçilmeden önce proje dizininde `cache/app.db` geçici olarak kullanılır.

---

## Sık Karşılaşılan Hatalar

| Hata | Çözüm |
|------|-------|
| `Bozuk ZIP dosyası` | ZIP bütünlüğünü kontrol edin (`zip -T dosya.zip`) |
| `XML parse hatası` | XML dosyasının geçerli UBL formatında olduğunu doğrulayın |
| `ModuleNotFoundError` | `pip install -r requirements.txt` komutunu tekrar çalıştırın |
| `Streamlit not found` | Sanal ortamı aktive edin: `source .venv/bin/activate` |

---

## requirements.txt

```
streamlit>=1.32.0
lxml>=5.1.0
pandas>=2.2.0
openpyxl>=3.1.0
bcrypt>=4.1.0
```

---

## Güvenlik Notu

Uygulama yalnızca yerel (localhost) erişim için tasarlanmıştır.
Harici ağa açmak için ek güvenlik önlemleri gereklidir.
