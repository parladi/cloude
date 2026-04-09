@echo off
chcp 65001 >nul
title Tiger Denetim Paneli v1.5
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
where python >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    echo      Python bulundu.
    goto :python_ok
)
where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=py
    echo      Python bulundu (py).
    goto :python_ok
)
echo.
echo  !!! HATA: Python bulunamadi !!!
echo  Python 3.11+ yukleyin: https://www.python.org/downloads/
echo  Kurulumda "Add Python to PATH" kutusunu isaretleyin!
echo.
echo  Devam etmek icin bir tusa basin...
pause >nul
exit /b 1

:python_ok

REM ---- NODE KONTROL ----
echo [2/5] Node.js kontrol ediliyor...
where node >nul 2>&1
if not %errorlevel%==0 (
    echo.
    echo  !!! HATA: Node.js bulunamadi !!!
    echo  Node.js 18+ yukleyin: https://nodejs.org/
    echo.
    echo  Devam etmek icin bir tusa basin...
    pause >nul
    exit /b 1
)
echo      Node.js bulundu.

REM ---- BACKEND KURULUM ----
echo [3/5] Backend hazirlaniyor...
cd backend
if not exist venv (
    echo      Python sanal ortam olusturuluyor...
    %PYTHON_CMD% -m venv venv
    if not exist venv (
        echo  !!! HATA: venv olusturulamadi !!!
        echo  Devam etmek icin bir tusa basin...
        pause >nul
        exit /b 1
    )
)
echo      pip install baslatiliyor...
call venv\Scripts\activate.bat
pip install -r requirements.txt 2>&1
echo      Backend OK
cd ..

REM ---- FRONTEND KURULUM ----
echo [4/5] Frontend hazirlaniyor...
cd frontend
if not exist node_modules (
    echo      npm install baslatiliyor (ilk sefer, 1-2 dakika bekleyin)...
    call npm install 2>&1
    if not exist node_modules (
        echo  !!! HATA: npm install basarisiz !!!
        echo  Devam etmek icin bir tusa basin...
        pause >nul
        exit /b 1
    )
)
echo      Frontend OK
cd ..

REM ---- CALISTIR ----
echo [5/5] Sunucular baslatiliyor...
echo.

REM Backend baslat - cmd /k ile pencere kapanmaz
cd backend
start "Tiger API" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
cd ..

echo  Backend baslatildi, 5 saniye bekleniyor...
timeout /t 5 /nobreak >nul

REM Frontend baslat - cmd /k ile pencere kapanmaz
cd frontend
start "Tiger UI" cmd /k "npx vite --host"
cd ..

echo  Frontend baslatildi, 5 saniye bekleniyor...
timeout /t 5 /nobreak >nul

echo.
echo  =============================================
echo   HAZIR! Tarayici aciliyor...
echo.
echo   Dashboard : http://localhost:5173
echo   API Docs  : http://localhost:8000/docs
echo.
echo   NOT: "Tiger API" ve "Tiger UI" pencerelerini
echo   kapatmayin - sunucular orada calisiyor.
echo  =============================================
echo.

start http://localhost:5173

echo  Bu pencereyi kapatabilirsiniz.
echo  Sunuculari durdurmak icin durdur.bat calistirin.
echo.
pause
