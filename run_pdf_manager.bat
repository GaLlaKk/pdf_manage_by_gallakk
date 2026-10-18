@echo off
setlocal

cd /d "%~dp0"

set "APP_PATH=%~dp0pdf_manager.py"
set "REQ_PATH=%~dp0requirements.txt"
set "VENV_PYTHON=%~dp0..\.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
) else (
    where py >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=py -3"
    ) else (
        where python >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_EXE=python"
        ) else (
            echo Python est introuvable.
            echo Installez Python 3 puis relancez ce fichier.
            pause
            exit /b 1
        )
    )
)

if /I "%PYTHON_EXE%"=="py -3" (
    py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 10))"
) else (
    "%PYTHON_EXE%" -c "import sys; raise SystemExit(sys.version_info < (3, 10))"
)
if errorlevel 1 (
    echo PDF Manager requires Python 3.10 or newer.
    pause
    exit /b 1
)

if exist "%REQ_PATH%" (
    if /I "%PYTHON_EXE%"=="py -3" (
        py -3 -c "import importlib.util, sys; sys.exit(not all(importlib.util.find_spec(module) for module in ('pypdf', 'cryptography', 'pymupdf', 'tkinterdnd2', 'PIL')))"
    ) else (
        "%PYTHON_EXE%" -c "import importlib.util, sys; sys.exit(not all(importlib.util.find_spec(module) for module in ('pypdf', 'cryptography', 'pymupdf', 'tkinterdnd2', 'PIL')))"
    )

    if errorlevel 1 (
        echo Installation des dependances manquantes...
        if /I "%PYTHON_EXE%"=="py -3" (
            py -3 -m pip install -r "%REQ_PATH%"
        ) else (
            "%PYTHON_EXE%" -m pip install -r "%REQ_PATH%"
        )

        if errorlevel 1 (
            echo Echec de l'installation des dependances.
            pause
            exit /b %errorlevel%
        )
    )
)

if not exist "%APP_PATH%" (
    echo Fichier d'application introuvable : %APP_PATH%
    pause
    exit /b 1
)

echo Lancement de PDF Manager by GaLlaKk...
if /I "%PYTHON_EXE%"=="py -3" (
    py -3 "%APP_PATH%"
) else (
    "%PYTHON_EXE%" "%APP_PATH%"
)

exit /b %errorlevel%
