# Forensik Panel

PARLADI METAL için yedek SQL Server veritabanları üzerinde ad-hoc SELECT sorguları
çalıştıran, sonuçları Excel tarzı tabloda gösteren ve her sorguyu arşivleyen
Flask tabanlı forensik analiz paneli.

## Hızlı Başlat (Windows)

1. Python 3.11 kurulu olmalı (https://www.python.org/downloads/)
2. `config\.env.example` dosyasını `config\.env` olarak kopyala ve SQL kimliklerini gir:
   ```
   FORENSIK_SQL_USER=sa
   FORENSIK_SQL_PASS=gercek_sifre
   FLASK_SECRET=rastgele-uzun-metin
   ```
3. Vendor dosyalarını indir (internet gerekli, bir kerelik):
   ```
   powershell -ExecutionPolicy Bypass -File scripts\download_vendor.ps1
   ```
4. `V1.bat` dosyasına çift tıkla. Tarayıcı otomatik açılır (`http://127.0.0.1:5151`).

## Klasör Yapısı

```
forensik-panel/
├── V1.bat                   # Başlatıcı
├── versions/v1/             # Kaynak kod
│   ├── app_v1.py            # Flask giriş
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/              # Blueprint'ler (7 sayfa)
│   ├── core/                # DB, SQL executor, arşiv, diff, export
│   ├── templates/           # Jinja2 şablonları
│   └── static/
│       ├── css/             # Tailwind + özel
│       └── vendor/          # Monaco, Tabulator (script ile indirilir)
├── config/
│   ├── config.yaml          # Uygulama ayarları, DB listesi
│   └── .env                 # SQL kimlikleri (git yoksayar)
├── data/
│   ├── archive/             # DuckDB + parquet sonuçları
│   ├── logs/                # app.log
│   └── output/              # İndirilen dosyalar
└── scripts/
    └── download_vendor.ps1  # Monaco + Tabulator + Tailwind indir
```

## Sayfalar

| URL | Açıklama |
|-----|----------|
| `/` | Panel (özet + son 10 sorgu) |
| `/databases/` | 12 yedek DB listesi + bağlantı testi |
| `/sql/` | SQL Editör (Monaco + Tabulator) |
| `/archive/` | Arşiv listesi, filtreleme |
| `/archive/<id>` | Arşiv detayı |
| `/diff/` | İki arşiv sorgusunu karşılaştır |
| `/settings/` | Ayarlar, bağlantı testi |
| `/debug/` | Canlı log + sistem + vendor kontrolü |

## Teknoloji

- **Python 3.11** (beta sürümleri değil)
- **Flask 3** + **Waitress** (production WSGI)
- **pymssql** (pyodbc değil — ODBC sorunları yaşandı)
- **Polars** (Pandas'tan hızlı)
- **DuckDB** + Parquet (arşiv)
- **Monaco Editor** (yerel, CDN değil) + textarea fallback
- **Tabulator** (Excel tarzı tablo)
- **Tailwind CSS** (standalone CLI ile derlenir)

## Güvenlik

- Yalnızca `SELECT` sorgularına izin verilir.
- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `EXEC` vb. reddedilir.
- SQL kimlikleri `.env` dosyasında, kodda asla yok.
- 127.0.0.1'e bağlı, dış ağdan erişilemez.

## Geliştirme

```bash
cd versions/v1
python3.11 -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate        # Windows

pip install -r requirements.txt
python app_v1.py
```

Tarayıcıdan `http://127.0.0.1:5151` aç.

## Log

Canlı log: `/debug/` sayfasında
Disk: `data/logs/app.log` (10 MB, 5 rotasyon)

## Sorun Giderme

**"Monaco yüklenemedi" diyor:**
`scripts\download_vendor.ps1` çalıştırılmamış. Basit textarea fallback otomatik devreye girer.

**"SQL kimlik bilgisi yok":**
`config\.env` yaratılmamış. `.env.example`'ı kopyala.

**Bağlantı hatası:**
SQL Server çalışıyor mu? TCP 1433 açık mı? `sa` şifresi doğru mu? `/settings/` sayfasından test et.

**Chrome "sayfa donuyor" diyor:**
Waitress çalıştığı için olmamalı. Eğer oluyorsa log'a bak: `data/logs/app.log`.

---

**Sürüm:** 1.0.0
**Lisans:** Dahili kullanım (PARLADI METAL)
