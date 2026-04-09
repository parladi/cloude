@echo off
chcp 65001 >nul
title Tiger Denetim Paneli - Kurulum
color 0B

echo.
echo  =============================================
echo   TIGER DENETIM PANELI - KURULUM
echo  =============================================
echo.

cd /d "%~dp0"

echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo  HATA: Python bulunamadi!
        echo  https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)
echo      Python OK

echo [2/4] Node.js kontrol ediliyor...
node --version >nul 2>&1
if errorlevel 1 (
    echo  HATA: Node.js bulunamadi!
    echo  https://nodejs.org/
    pause
    exit /b 1
)
echo      Node.js OK

echo [3/4] Backend kuruluyor...
cd backend
if not exist venv (
    %PYTHON_CMD% -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..
echo      Backend OK

echo [4/4] Frontend kuruluyor...
cd frontend
call npm install
cd ..
echo      Frontend OK

echo.
echo  =============================================
echo   KURULUM TAMAMLANDI!
echo   Calistirmak icin: baslat.bat
echo  =============================================
pause
