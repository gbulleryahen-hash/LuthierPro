@echo off
cd /d "%~dp0"
python main.py
IF ERRORLEVEL 1 (
    echo.
    echo Erreur au lancement. Assurez-vous d'avoir lancé installer.bat d'abord.
    pause
)
