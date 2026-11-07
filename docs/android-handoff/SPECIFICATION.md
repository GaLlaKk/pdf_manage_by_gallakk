# PDF Manager Android — spécification fonctionnelle

Cette spécification décrit le comportement de l'application de bureau
[PDF Manager by GaLlaKk](https://github.com/GaLlaKk/pdf_manage_by_gallakk)
(Python/Tkinter) afin de produire une version **Android native (Kotlin)**
équivalente. Source de vérité : `pdf_manager_service.py` et `tests/` du dépôt
d'origine. En cas de doute, lire ce code.

## 1. Principes non négociables

1. **100 % local** : aucune permission `INTERNET`, aucun SDK de télémétrie,
   d'analytics, de publicité ou de crash reporting réseau. Le dépôt d'origine
   possède un test qui interdit les modules réseau.
2. **Le fichier source n'est jamais modifié.** Compression et rotation écrivent
   un fichier distinct et refusent d'écraser la source.
3. **Écriture atomique** : écrire dans un fichier temporaire du même dossier,
   puis renommer. Supprimer le temporaire en cas d'échec.
4. **Opérations longues hors du thread principal** (coroutines, `Dispatchers.IO`)
   avec indicateur de progression et annulation possible.
5. **Aucune version codée en dur** : `versionName` dérive du tag Git `v*`
   (injecté par Gradle/CI).

## 2. Fonctionnalités

### 2.1 Fusion
- L'utilisateur sélectionne plusieurs PDF (sélecteur de documents multiple, ajout
  répétable) et peut **réordonner** (monter/descendre, glisser-déposer) et
  **retirer** des éléments.
- La fusion respecte **strictement l'ordre de la liste**.
- Les rotations définies dans l'aperçu (§2.4) sont **appliquées à la fusion**.
- Sortie : fichier choisi via `ACTION_CREATE_DOCUMENT` (`application/pdf`).
- Erreurs : liste vide → « Aucun PDF sélectionné » ; fichier illisible → erreur
  explicite, sortie non créée.

### 2.2 Découpe
- Un PDF en entrée, un dossier de sortie (`ACTION_OPEN_DOCUMENT_TREE`).
- Un fichier **par page** nommé `{nom_sans_extension}_{n}.pdf`.
- `n` est **rempli de zéros à gauche** selon le nombre total de pages :
  largeur = nombre de chiffres du total (3 pages → `_1`, `_2`, `_3` ;
  12 pages → `_01` … `_12` ; 123 pages → `_001` … `_123`).
- PDF vide ou invalide → erreur.
- Résultat : nombre de fichiers générés et dossier de destination.

### 2.3 Compression
- Un PDF en entrée, sortie distincte (`.pdf` obligatoire, différente de la source).
- Deux modes :
  - `lossless` (« Sans perte ») : optimise la structure (flux compressés,
    objets inutilisés supprimés, polices/images déjà compressées), sans toucher
    à la qualité des images.
  - `balanced` (« Équilibré ») : en plus, **recompresse les images dont la
    résolution dépasse 200 dpi vers 150 dpi, JPEG qualité 65**
    (PyMuPDF : `rewrite_images(dpi_threshold=200, dpi_target=150, quality=65,
    lossy=True, lossless=True, bitonal=False)`), puis sauvegarde optimisée
    (`garbage=4, clean, deflate`).
- Mode inconnu → erreur. Afficher après succès : taille originale, taille
  compressée, chemin.
- Si le PDF compressé est plus gros que l'original, informer l'utilisateur.

### 2.4 Aperçu et rotation
- Aperçu page par page (navigation « Page X / Y ») du fichier sélectionné.
- Rotation d'une page par pas de ±90° (`rotate_left` / `rotate_right`).
- Les rotations sont **temporaires** (état en mémoire, par fichier et par page)
  jusqu'à : (a) l'enregistrement d'une **copie pivotée** (nom proposé
  `{nom}_rotated.pdf`) ou (b) la fusion.
- Modèle de données : `Map<fichier, Map<indexPage(0-based), rotation>>` avec
  rotation ∈ {90, 180, 270} ; une rotation revenue à 0° est **supprimée** de la
  map, et la map du fichier vide est supprimée.
- Validation à l'application : index entier ≥ 0 et < nombre de pages, rotation
  ∈ {0, 90, 180, 270}, sinon erreur. La rotation est **ajoutée** à celle déjà
  présente dans la page (delta).
- « Enregistrer une copie pivotée » désactivé tant qu'aucune rotation n'existe.

### 2.5 Langues
11 langues : fr, en, de, es, pt, zh, ja, ru, ar, ko, hi (arabe = **RTL**).
Les chaînes sont déjà exportées en ressources Android (`res/values*/strings.xml`,
voir §5). Suivre la langue du système, avec sélecteur dans l'application
(`AppCompatDelegate.setApplicationLocales`) si souhaité.

## 3. Correspondance Desktop → Android

| Desktop (Tkinter)                  | Android natif                                            |
|------------------------------------|----------------------------------------------------------|
| Onglets Fusionner/Diviser/Compresser | `NavigationBar` + 3 écrans (Compose) ou onglets         |
| Boîtes de dialogue fichiers        | Storage Access Framework (`OpenMultipleDocuments`, `CreateDocument`, `OpenDocumentTree`) |
| Chemins de fichiers                | `Uri` (`content://`), jamais de chemin absolu ; copier vers le cache si la bibliothèque exige un `File` |
| Glisser-déposer de fichiers        | Intent « Ouvrir avec / Partager vers » (`ACTION_VIEW`, `ACTION_SEND(_MULTIPLE)`) |
| Fenêtre de chargement              | Indicateur de progression + bouton annuler               |
| `messagebox`                       | Snackbar / dialogue Material                             |
| Aperçu (PyMuPDF)                   | `android.graphics.pdf.PdfRenderer`                       |
| `pypdf` (fusion/découpe/rotation)  | PdfBox-Android (`com.tom-roush:pdfbox-android`) ou équivalent |
| PyMuPDF (compression)              | voir §4                                                  |

## 4. Points techniques à trancher

- **Compression** : c'est le point le plus difficile.
  - `lossless` : PdfBox-Android (`PDDocument.save` avec flux compressés) suffit.
  - `balanced` : PdfBox ne recompresse pas les images nativement. Itérer sur les
    `PDImageXObject`, estimer le dpi effectif, rééchantillonner à 150 dpi et
    réencoder en JPEG q65 (`JPEGFactory`). Alternative : MuPDF (**licence AGPL**
    : vérifier la compatibilité avant de l'adopter, PyMuPDF l'est aussi).
- **Mémoire** : ne jamais charger de gros PDF entièrement ; fermer les
  `PdfRenderer.Page`, recycler les `Bitmap`, traiter page par page à la découpe.
- **Fichiers d'entrée** : `PdfRenderer` demande un `ParcelFileDescriptor`
  seekable ; copier dans le cache si le flux ne l'est pas.
- **Licences** : lister les licences des dépendances (Apache-2.0 attendu).
- **Distribution** : Play Store (AAB signé) + APK en pièce jointe de release.

## 5. Ressources fournies

- `res/values*/strings.xml` : 11 langues, générées depuis
  `pdf_manager_translations.py` par `scripts/export_android_strings.py`.
  - Clés identiques au desktop (sauf `label` → `language_name`).
  - Placeholders nommés `{path}` convertis en positionnels `%1$s` (ordre de
    première apparition dans la chaîne anglaise). Utiliser
    `getString(R.string.page_label, current, total)`.
  - Certaines chaînes mentionnent « fenêtre », « glisser-déposer » ou
    « octets » : à relire/adapter pour mobile (voir `drop_files_hint`,
    `add_folder`, etc.) **dans le dépôt Android** (ne pas modifier les fichiers
    générés à la main : adapter le contenu côté Android et le documenter).
- Icônes : `assets/icons/*.ico` (logo source). Générer une icône adaptative
  (`mipmap-anydpi-v26`) à partir du logo 256×256 ; demander un SVG/PNG
  haute résolution si la qualité est insuffisante.

## 6. Tests attendus (parité avec le desktop)

Reprendre les cas de `tests/test_pdf_manager_service.py` en tests
instrumentés/JVM :
- fusion dans l'ordre sélectionné, avec et sans rotations ;
- découpe : nombre de fichiers, nommage avec zéros de remplissage ;
- rotation : source inchangée, refus de sortie = source, rotation invalide ;
- compression : modes valides/invalides, source inchangée, fichier temporaire
  supprimé après échec ;
- cohérence des chaînes : mêmes clés et mêmes placeholders dans toutes les langues.

## 7. Plan de livraison suggéré

1. Projet Gradle (Kotlin, Compose, minSdk 26+, targetSdk courant), CI GitHub
   Actions (lint + tests + `assembleRelease`).
2. Couche `pdf/` pure Kotlin (équivalent de `pdf_manager_service.py`) + tests.
3. Écran Fusion (sélection, ordre, aperçu, rotation) puis Découpe puis
   Compression.
4. Localisation (importer `res/`), RTL, accessibilité (TalkBack, tailles).
5. Intents entrants (Ouvrir avec / Partager), polish Material 3 (mode sombre).
6. Release signée (`android-v*` ou `v*` dans le nouveau dépôt), checksums.
