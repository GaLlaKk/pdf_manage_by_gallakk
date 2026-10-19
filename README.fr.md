# PDF Manager par GaLlaKk

Une application de bureau Python pour fusionner, séparer, compresser, faire pivoter et réorganiser les pages de fichiers PDF. L'application fonctionne localement : vous pouvez gérer vos PDF sans téléverser ni partager vos documents privés avec un service en ligne.

## Lire dans une autre langue

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## Fonctionnalités

- Fusionner plusieurs PDF en un seul document.
- Séparer un PDF en pages individuelles.
- Compresser les PDF en mode sans perte ou équilibré.
- Faire pivoter et réorganiser les pages avant l'enregistrement.
- Suivre la progression des opérations longues.

## Téléchargements

Pour chaque version publiée avec une étiquette `v*`, GitHub Actions crée des packages autonomes pour Windows, Linux et macOS. Téléchargez le package correspondant à votre système dans la section **Assets** de la page [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) ; Python n'a pas besoin d'être installé.

La version de l'application est affichée dans le titre de la fenêtre. L'icône est incluse dans l'exécutable Windows et le bundle macOS ; elle est également utilisée dans la fenêtre de l'application, la boîte de dialogue de chargement et la barre des tâches.

Sur macOS, le premier lancement peut nécessiter une autorisation dans **Réglages Système → Confidentialité et sécurité**, car l'application n'est ni signée ni notariée. Les packages Linux ciblent l'architecture indiquée dans leur nom et nécessitent un environnement de bureau graphique avec prise en charge de Tk.

## Versions et publications

`pdf_manager_version.py` est la source unique de la version affichée par l'application. Pour publier une version, mettez à jour `__version__` dans ce fichier, puis créez et poussez une étiquette Git correspondante préfixée par `v`. Par exemple, pour la version `1.0.0` :

```bash
git tag v1.0.0
git push origin v1.0.0
```

Le même workflow peut être lancé manuellement depuis l'onglet **Actions** du dépôt ; les packages créés sont alors disponibles comme artefacts du workflow.

## Lancer depuis les sources

Installez Python 3.10 ou une version ultérieure ainsi que les dépendances, puis lancez l'application :

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

Pour lancer les tests :

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## Organisation du projet

- `pdf_manager.py` : point d'entrée de l'application et orchestration de la fenêtre principale.
- `pdf_manager_ui/` : interface regroupée par fonctions de fusion, séparation, compression et aperçu.
- `assets/icons/` : fichiers source des icônes de l'application.
- `scripts/` : scripts autonomes de compilation et de création des packages de publication.
- `tests/` : tests de l'application et du service PDF.
- `pdf_manager_version.py` : version affichée dans l'application.
