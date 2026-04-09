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

echo  Klasor: %cd%
echo.

REM ---- PYTHON KONTROL ----
echo [1/5] Python kontrol ediliyor...
python --version 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=python
    goto python_ok
)
py --version 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=py
    goto python_ok
)
echo.
echo  HATA: Python bulunamadi!
echo  Python yukleyin: https://www.python.org/downloads/
echo  Kurulumda "Add Python to PATH" isaretleyin!
echo.
goto bitti

:python_ok
echo.

REM ---- NODE KONTROL ----
echo [2/5] Node.js kontrol ediliyor...
node --version 2>nul
if not %errorlevel%==0 (
    echo.
    echo  HATA: Node.js bulunamadi!
    echo  Node.js yukleyin: https://nodejs.org/
    echo.
    goto bitti
)
echo.

REM ---- BACKEND KURULUM ----
echo [3/5] Backend hazirlaniyor...
cd backend
if not exist venv (
    echo  venv olusturuluyor...
    %PYTHON_CMD% -m venv venv
)
if not exist venv\Scripts\activate.bat (
    echo  HATA: venv olusturulamadi!
    cd ..
    goto bitti
)
call venv\Scripts\activate.bat
echo  pip install basliyor...
pip install -r requirements.txt
echo  Backend OK
echo.
cd ..

REM ---- FRONTEND KURULUM ----
echo [4/5] Frontend hazirlaniyor...
cd frontend
if not exist node_modules (
    echo  npm install basliyor (1-2 dk bekleyin)...
    call npm install
)
if not exist node_modules (
    echo  HATA: npm install basarisiz!
    cd ..
    goto bitti
)
echo  Frontend OK
echo.
cd ..

REM ---- SUNUCULARI BASLAT ----
echo [5/5] Sunucular baslatiliyor...
echo.

echo  Backend baslatiliyor (port 8000)...
cd backend
start "Tiger API" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
cd ..

echo  5 saniye bekleniyor...
ping 127.0.0.1 -n 6 >nul

echo  Frontend baslatiliyor (port 5173)...
cd frontend
start "Tiger UI" cmd /k "npx vite --host"
cd ..

echo  5 saniye bekleniyor...
ping 127.0.0.1 -n 6 >nul

echo.
echo  =============================================
echo   HAZIR! Tarayici aciliyor...
echo.
echo   Dashboard : http://localhost:5173
echo   API       : http://localhost:8000/docs
echo.
echo   "Tiger API" ve "Tiger UI" pencerelerini
echo   kapatmayin!
echo  =============================================
echo.

start http://localhost:5173

:bitti
echo.
echo  ---- BU PENCERE KAPANMAYACAK ----
echo  Bir tusa basin...
pause >nul
echo  Tekrar bir tusa basin...
pause >nul
