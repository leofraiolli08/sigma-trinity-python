@echo off
setlocal
cd /d "%~dp0"
title SIGMA TRINITY V10 - Verificar instalacao
where py >nul 2>nul
if not errorlevel 1 (
    py main.py --diagnose
) else (
    python main.py --diagnose
)
echo.
pause
endlocal
