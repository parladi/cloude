@echo off
chcp 65001 >nul
title Tiger Denetim Paneli - Durdur

echo Sunucular durduruluyor...

REM uvicorn ve node islemlerini kapat
taskkill /FI "WINDOWTITLE eq Tiger API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Tiger UI*" /F >nul 2>&1

REM Port bazli da temizle
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Tum sunucular durduruldu.
timeout /t 2 /nobreak >nul
