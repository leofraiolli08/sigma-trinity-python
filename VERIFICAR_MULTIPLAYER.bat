@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SIGMA TRINITY V10 - Diagnostico Multiplayer
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 multiplayer_diagnostic.py
) else (
    python multiplayer_diagnostic.py
)
echo.
echo Relatorio: DIAGNOSTICO_MULTIPLAYER.txt
echo Logs: logs\multiplayer.log
pause
