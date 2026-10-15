@echo off
cd /d "%~dp0"
if not exist "assets\music" mkdir "assets\music"
start "" "%~dp0assets\music"
