# ============================================================
# Launch script - GaLlaKk
# Vérifie les dépendances puis démarre l'application de fusion PDF
# ============================================================

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
$requirementsFile = Join-Path $scriptDir 'requirements.txt'
$appFile = Join-Path $scriptDir 'pdf_manager.py'

if (-not (Test-Path $pythonExe)) {
    Write-Host "Python 3.10 introuvable dans le dossier standard Windows." -ForegroundColor Yellow
    Write-Host "Vérifiez que Python est installé, puis relancez ce script." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

if (Test-Path $requirementsFile) {
    Write-Host "Installation des dépendances..." -ForegroundColor Cyan
    & $pythonExe -m pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "L'installation des dépendances a échoué." -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour quitter"
        exit $LASTEXITCODE
    }
}

if (-not (Test-Path $appFile)) {
    Write-Host "Le fichier pdf_manager.py est introuvable dans le dossier de l'application." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host "Lancement de PDF Manager by GaLlaKk..." -ForegroundColor Green
& $pythonExe $appFile
exit $LASTEXITCODE
