@echo off
chcp 65001 >nul
title Tiger Denetim - Kurulum
color 0B
echo.
echo  TIGER DENETIM PANELI - KURULUM
echo.
cd /d "%~dp0"

python --version 2>nul
if %errorlevel%==0 (set PYTHON_CMD=python) else (set PYTHON_CMD=py)

echo Backend kuruluyor...
cd backend
if not exist venv %PYTHON_CMD% -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo Frontend kuruluyor...
cd frontend
call npm install
cd ..

echo.
echo  KURULUM TAMAMLANDI!
pause
