@echo off
chcp 65001 >nul
title Tiger Denetim Paneli
color 0B

echo ============================================
echo   TIGER DENETIM PANELI BASLATILIYOR
echo ============================================
echo.

REM Proje klasorune git
cd /d "%~dp0"

REM Ilk kurulum yapilmamissa otomatik kur
if not exist "backend\venv" (
    echo Ilk calistirma - kurulum yapiliyor...
    call kur.bat
)
if not exist "frontend\node_modules" (
    echo Ilk calistirma - kurulum yapiliyor...
    call kur.bat
)

echo [1/2] Backend baslatiliyor (port 8000)...
cd backend
start "Tiger API" cmd /k "call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000"
cd ..

REM Backend'in ayaga kalkmasi icin kisa bekle
timeout /t 3 /nobreak >nul

echo [2/2] Frontend baslatiliyor (port 5173)...
cd frontend
start "Tiger UI" cmd /k "npm run dev"
cd ..

REM Frontend'in ayaga kalkmasi icin kisa bekle
timeout /t 4 /nobreak >nul

echo.
echo ============================================
echo   HAZIR! Tarayici aciliyor...
echo.
echo   Dashboard:  http://localhost:5173
echo   API:        http://localhost:8000/docs
echo.
echo   Kapatmak icin: durdur.bat
echo ============================================

start http://localhost:5173

pause
