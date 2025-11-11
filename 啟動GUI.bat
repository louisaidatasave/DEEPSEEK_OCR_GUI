@echo off
chcp 65001 >nul
echo 正在啟動 DeepSeek-OCR GUI...
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat
python scripts\gui_app.py

pause
