# ============================================================
# Launch script - GaLlaKk
# Vérifie les dépendances puis démarre l'application de fusion PDF
# ============================================================

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir '..\.venv\Scripts\python.exe'
$requirementsFile = Join-Path $scriptDir 'requirements.txt'
$appFile = Join-Path $scriptDir 'pdf_manager.py'
$pythonArgs = @()

if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command py).Source
    $pythonArgs = @('-3')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command python).Source
} else {
    Write-Host "Python 3.10 ou supérieur est introuvable." -ForegroundColor Yellow
    Write-Host "Installez Python, puis relancez ce script." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

& $pythonExe @pythonArgs -c "import sys; raise SystemExit(sys.version_info < (3, 10))"
if ($LASTEXITCODE -ne 0) {
    Write-Host "PDF Manager nécessite Python 3.10 ou supérieur." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit $LASTEXITCODE
}

if (Test-Path $requirementsFile) {
    & $pythonExe @pythonArgs -c "import importlib.util, sys; sys.exit(not all(importlib.util.find_spec(module) for module in ('pypdf', 'cryptography', 'pymupdf', 'tkinterdnd2', 'PIL')))"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installation des dépendances manquantes..." -ForegroundColor Cyan
        & $pythonExe @pythonArgs -m pip install -r $requirementsFile
        if ($LASTEXITCODE -ne 0) {
            Write-Host "L'installation des dépendances a échoué." -ForegroundColor Red
            Read-Host "Appuyez sur Entrée pour quitter"
            exit $LASTEXITCODE
        }
    }
}

if (-not (Test-Path $appFile)) {
    Write-Host "Le fichier pdf_manager.py est introuvable dans le dossier de l'application." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Set-Location $scriptDir
Write-Host "Lancement de PDF Manager by GaLlaKk..." -ForegroundColor Green
& $pythonExe @pythonArgs $appFile
exit $LASTEXITCODE
