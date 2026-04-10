@echo off
chcp 65001 >nul
title Tiger Denetim - Durdur
echo Sunucular durduruluyor...
taskkill /FI "WINDOWTITLE eq Tiger API*" /F >/dev/null 2>&1
taskkill /FI "WINDOWTITLE eq Tiger UI*" /F >/dev/null 2>&1
for /f "tokens=5" %%a in (netstat -ano | findstr :8000 | findstr LISTENING) do taskkill /PID %%a /F >/dev/null 2>&1
for /f "tokens=5" %%a in (netstat -ano | findstr :5173 | findstr LISTENING) do taskkill /PID %%a /F >/dev/null 2>&1
echo Durduruldu.
pause
