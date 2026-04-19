@echo off
setlocal
cd /d "%~dp0versions\v1"
title Forensik Panel v1

echo ==========================================
echo   FORENSIK PANEL v1 BASLATILIYOR
echo ==========================================
echo.

py -3.11 -V >nul 2>&1
if errorlevel 1 (
    echo HATA: Python 3.11 bulunamadi.
    echo Lutfen Python 3.11 kurun: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Paketler kontrol ediliyor...
py -3.11 -c "import flask, pymssql, polars, duckdb, waitress" >nul 2>&1
if errorlevel 1 (
    echo Eksik paketler kuruluyor (ilk baslatmada bir kerelik)...
    py -3.11 -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo Paket kurulumu basarisiz. Internet var mi kontrol edin.
        pause
        exit /b 1
    )
)

echo Tarayici aciliyor (3 saniye icinde)...
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5151'"

echo.
echo Uygulama baslatiliyor...
echo Kapatmak icin bu pencereye donup Ctrl+C yapabilirsiniz.
echo.

py -3.11 app_v1.py

pause
