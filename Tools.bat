@echo off
setlocal
cd /d "%~dp0"
python tools_launcher.py
if errorlevel 1 pause
