@echo off
setlocal
cd /d "%~dp0"
rem Prefer pythonw.exe so the GUI launches without a console window.
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "%~dp0tools_launcher.py"
) else (
  rem No pythonw on PATH: run via python; the launcher re-launches itself
  rem windowless if it can, otherwise falls back to showing a console.
  python "%~dp0tools_launcher.py"
)
