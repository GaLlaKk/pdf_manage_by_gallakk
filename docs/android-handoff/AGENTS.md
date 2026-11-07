# Guide du projet pour les agents

> Modèle à copier à la racine du nouveau dépôt Android sous le nom `AGENTS.md`,
> avec `SPECIFICATION.md` (dans `docs/`) et le dossier `res/`.

## Objectif

PDF Manager Android est la version **native (Kotlin)** de
[PDF Manager by GaLlaKk](https://github.com/GaLlaKk/pdf_manage_by_gallakk).
Elle fusionne, découpe, compresse, prévisualise et fait pivoter des PDF
**localement**, sans aucun service en ligne.

Le comportement attendu est décrit dans `docs/SPECIFICATION.md` : le lire en
premier. Le dépôt de référence (Python) fait foi pour la logique PDF :
`pdf_manager_service.py` et `tests/test_pdf_manager_service.py`.

## Règles impératives

- **Pas de permission `INTERNET`**, pas de bibliothèque réseau, d'analytics ou
  de publicité. Ajouter un test (ou une vérification Gradle du manifeste fusionné)
  qui échoue si la permission apparaît.
- Les PDF source ne sont **jamais modifiés** ; compression et rotation créent un
  fichier distinct, via un fichier temporaire puis renommage.
- Accès aux fichiers par **Storage Access Framework** (`Uri`), sans
  `MANAGE_EXTERNAL_STORAGE` ni `READ/WRITE_EXTERNAL_STORAGE`.
- Opérations PDF hors du thread principal, annulables, avec progression.
- Pas de version codée en dur : `versionName` vient du tag Git.
- Toute chaîne visible passe par `strings.xml` ; garder les mêmes clés et
  placeholders dans les 11 langues (fr, en, de, es, pt, zh, ja, ru, ar, ko, hi).
  Le layout doit fonctionner en RTL (arabe).

## Architecture recommandée

- `app/` : UI Jetpack Compose (Material 3), un écran par fonction
  (Fusion, Découpe, Compression) + aperçu.
- `pdf/` : logique PDF pure Kotlin, sans dépendance Android UI,
  testable en JVM. Équivalent de `pdf_manager_service.py` :
  `mergePdfs`, `splitPdfPages`, `compressPdf`, `rotatePdfPages`, `isPdfFile`.
- Séparation UI / logique PDF identique au dépôt de référence : l'UI ne
  manipule pas directement les bibliothèques PDF.
- Rotations de prévisualisation temporaires (état en mémoire) jusqu'à
  l'enregistrement d'une copie ou à la fusion.

## Ressources issues du dépôt de référence

- `res/values*/strings.xml` sont **générés** par
  `scripts/export_android_strings.py` du dépôt de référence. Pour les
  mettre à jour, relancer le script là-bas puis recopier `res/` ; ne pas
  diverger silencieusement.
- Les chaînes pensées pour le desktop (glisser-déposer, fenêtre, dossiers)
  peuvent être adaptées pour le mobile, dans toutes les langues à la fois.

## Développement et validation

À compléter dès la création du projet Gradle, par exemple :

```bash
./gradlew lintDebug testDebugUnitTest
./gradlew assembleDebug
```

JDK 17+ et Android Studio (ou SDK en ligne de commande) requis. Toute
modification de la logique PDF s'accompagne d'un test de parité avec les cas
de `tests/test_pdf_manager_service.py` du dépôt de référence.

## Releases

Un tag `v*` du dépôt déclenche le CI : lint, tests, build `release` signé
(secrets du keystore dans GitHub Secrets, jamais dans le dépôt), publication
de l'APK/AAB et de `SHA256SUMS.txt`. Vérifier que le tag est sur `main`.
