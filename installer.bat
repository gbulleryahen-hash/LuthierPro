@echo off
echo ========================================
echo   LuthierPro — Installation
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERREUR : Python n'est pas installé.
    echo Téléchargez Python sur https://www.python.org/downloads/
    echo Cochez "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

echo Python détecté. Installation des dépendances...
echo.
pip install PySide6 reportlab

echo.
echo ========================================
echo   Installation terminée !
echo   Lancez LuthierPro avec : lancer.bat
echo ========================================
pause
