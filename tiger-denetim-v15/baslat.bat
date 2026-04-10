@echo off
chcp 65001 >nul
title Tiger Denetim Paneli v1.5
color 0B

echo.
echo  =============================================
echo   TIGER DENETIM PANELI v1.5
echo  =============================================
echo.

cd /d "%~dp0"

echo  Klasor: %cd%
echo.

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
echo  https://www.python.org/downloads/
goto bitti

:python_ok
echo.

echo [2/5] Node.js kontrol ediliyor...
node --version 2>nul
if not %errorlevel%==0 (
    echo  HATA: Node.js bulunamadi!
    echo  https://nodejs.org/
    goto bitti
)
echo.

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
echo  =============================================

start http://localhost:5173

:bitti
echo.
echo  Bir tusa basin...
pause >nul
echo  Tekrar bir tusa basin...
pause >nul
