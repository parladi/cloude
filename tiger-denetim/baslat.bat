@echo off
chcp 65001 >nul
title Tiger Denetim Paneli
color 0B

echo.
echo  =============================================
echo   TIGER DENETIM PANELI v1.5
echo  =============================================
echo.

REM Proje klasorune git
cd /d "%~dp0"

REM ---- PYTHON KONTROL ----
echo [1/5] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  HATA: Python bulunamadi!
        echo  Python 3.11+ yukleyin: https://www.python.org/downloads/
        echo  Kurulumda "Add Python to PATH" kutusunu isaretleyin!
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)
echo      Python OK

REM ---- NODE KONTROL ----
echo [2/5] Node.js kontrol ediliyor...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  HATA: Node.js bulunamadi!
    echo  Node.js 18+ yukleyin: https://nodejs.org/
    echo  LTS surumunu indirin.
    echo.
    pause
    exit /b 1
)
echo      Node.js OK

REM ---- BACKEND KURULUM ----
echo [3/5] Backend hazirlaniyor...
cd backend
if not exist venv (
    echo      Python venv olusturuluyor...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo  HATA: Python venv olusturulamadi!
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat 2>nul
pip install -r requirements.txt --quiet 2>nul
if errorlevel 1 (
    echo      pip install tekrar deneniyor...
    pip install -r requirements.txt
)
echo      Backend OK
cd ..

REM ---- FRONTEND KURULUM ----
echo [4/5] Frontend hazirlaniyor...
cd frontend
if not exist node_modules (
    echo      npm install calistiriliyor (ilk sefer, biraz bekleyin)...
    call npm install
    if errorlevel 1 (
        echo  HATA: npm install basarisiz!
        echo  Node.js ve npm versiyonunuzu kontrol edin.
        pause
        exit /b 1
    )
)
echo      Frontend OK
cd ..

REM ---- CALISTIR ----
echo [5/5] Sunucular baslatiliyor...
echo.

REM Onceki islemleri temizle
taskkill /FI "WINDOWTITLE eq Tiger API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Tiger UI*" /F >nul 2>&1

REM Backend baslat
cd backend
start "Tiger API" cmd /c "call venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1"
cd ..

REM Backend icin bekle
echo  Backend baslatiliyor...
timeout /t 4 /nobreak >nul

REM Frontend baslat
cd frontend
start "Tiger UI" cmd /c "npx vite --host 2>&1"
cd ..

REM Frontend icin bekle
echo  Frontend baslatiliyor...
timeout /t 5 /nobreak >nul

echo.
echo  =============================================
echo   HAZIR! Tarayici aciliyor...
echo.
echo   Dashboard : http://localhost:5173
echo   API Docs  : http://localhost:8000/docs
echo.
echo   Kapatmak icin bu pencereyi kapatin
echo   veya durdur.bat calistirin.
echo  =============================================
echo.

start http://localhost:5173

echo  Cikis icin bir tusa basin...
pause >nul
