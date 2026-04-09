@echo off
chcp 65001 >nul
title Tiger Denetim Paneli - Ilk Kurulum
color 0B

echo ============================================
echo   TIGER DENETIM PANELI - ILK KURULUM
echo ============================================
echo.

REM Proje klasorune git
cd /d "%~dp0"

echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi! Python 3.11+ yukleyin.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
echo      Python OK

echo [2/4] Node.js kontrol ediliyor...
node --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Node.js bulunamadi! Node.js 18+ yukleyin.
    echo https://nodejs.org/
    pause
    exit /b 1
)
echo      Node.js OK

echo [3/4] Backend bagimliliklari yukleniyor...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
cd ..
echo      Backend OK

echo [4/4] Frontend bagimliliklari yukleniyor...
cd frontend
call npm install --silent
cd ..
echo      Frontend OK

echo.
echo ============================================
echo   KURULUM TAMAMLANDI!
echo   Calistirmak icin: baslat.bat
echo ============================================
pause
