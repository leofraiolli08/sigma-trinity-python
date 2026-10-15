@echo off
setlocal
cd /d "%~dp0"
title SIGMA TRINITY V10 - LENDAS + EXPEDICOES
echo SIGMA TRINITY V10 - LENDAS + EXPEDICOES
echo Pasta aberta: %CD%
echo.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
    goto :resultado
)
where py >nul 2>nul
if not errorlevel 1 (
    py main.py
) else (
    python main.py
)
:resultado
if errorlevel 1 (
    echo.
    echo Nao foi possivel iniciar. Confira o README.md.
    echo Instale a dependencia com: python -m pip install -r requirements.txt
    pause
)
endlocal
