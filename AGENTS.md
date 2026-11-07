# Guide du projet pour les agents

## Objectif

PDF Manager by GaLlaKk est une application de bureau Python/Tkinter qui traite les PDF localement. Elle permet de fusionner, découper, compresser, prévisualiser, réorganiser et faire pivoter des pages. Aucun service en ligne n'est utilisé pour les opérations sur les documents.

## Architecture

- `pdf_manager.py` est le point d'entrée. Il crée la fenêtre Tkinter, choisit la langue, assemble les onglets et exécute les tâches longues dans un thread avec une fenêtre de chargement.
- `pdf_manager_ui/` contient les comportements d'interface sous forme de mixins :
  - `merge.py` : sélection, ordre, aperçu et fusion des fichiers.
  - `split.py` : choix du PDF et du dossier de sortie pour le découpage.
  - `compress.py` : choix du mode et compression.
  - `preview.py` : aperçu des pages, rotations temporaires et enregistrement d'une copie pivotée.
- `pdf_manager_service.py` contient les opérations PDF réutilisables par l'interface : `merge_pdfs`, `split_pdf_pages`, `compress_pdf`, `rotate_pdf_pages` et `is_pdf_file`.
- `pdf_manager_translations.py` contient les chaînes de l'interface. Les traductions doivent garder les mêmes clés et les mêmes paramètres de format dans toutes les langues.
- `pdf_manager_version.py` déduit la version affichée du tag Git (`_build_version.py`, généré à la construction, sinon `git describe`).
- `assets/icons/` contient les icônes sources. `scripts/build_application.py` les prépare et construit l'application autonome ; `scripts/package_release.py` archive le résultat.
- `tests/` couvre le service PDF, les traductions et quelques comportements de l'application.
- `.github/workflows/ci.yml` lance les tests (PR, `main`, appel depuis le CD). `.github/workflows/cd.yml` s'exécute sur un tag `v*` : vérifie que le tag est sur `main`, lance le CI, construit les packages Windows, Linux et macOS, puis publie la release avec `SHA256SUMS.txt`.

## Repères de maintenance

- Garder la logique de traitement PDF dans `pdf_manager_service.py` et l'interaction Tkinter dans les mixins d'interface.
- Les fichiers source doivent rester inchangés lors de la compression et de la rotation : ces opérations produisent un fichier de sortie distinct et refusent d'écraser la source.
- La fusion respecte l'ordre de `selected_files` et applique les rotations de prévisualisation transmises à `merge_pdfs`.
- Les rotations de prévisualisation sont temporaires jusqu'à l'enregistrement d'une copie pivotée ou à la fusion.
- Lors de l'ajout ou de la modification d'une chaîne d'interface, mettre à jour toutes les langues dans `pdf_manager_translations.py`. Le test de cohérence des traductions vérifie les clés et les champs de format.
- La version vient du tag Git `v*` : pas de version codée en dur ; `scripts/build_application.py --version <tag>` l'intègre dans l'application.

## Développement et validation

Python 3.11 ou plus récent est requis. Depuis la racine du dépôt :

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

Pour installer les dépendances de test et lancer la suite :

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

`requirements-build.txt` inclut les dépendances de l'application ainsi que pytest et PyInstaller. La construction autonome s'effectue sur la plateforme cible avec :

```bash
python scripts/build_application.py
python scripts/package_release.py --platform windows
```

Pour les autres plateformes, remplacer `windows` par `linux` ou `macos`. Le script de packaging attend que la construction ait déjà produit les fichiers dans `dist/`.
