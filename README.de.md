# PDF Manager von GaLlaKk

Eine Python-Desktopanwendung zum Zusammenführen, Teilen, Komprimieren, Drehen und Neuanordnen von PDF-Seiten. Die Anwendung läuft lokal: Sie können Ihre PDFs verwalten, ohne private Dokumente bei einem Onlinedienst hochzuladen oder zu teilen.

## In einer anderen Sprache lesen

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## Funktionen

- Mehrere PDFs zu einem Dokument zusammenführen.
- Ein PDF in einzelne Seiten aufteilen.
- PDFs verlustfrei oder im ausgewogenen Modus komprimieren.
- Seiten vor dem Speichern drehen und neu anordnen.
- Den Fortschritt länger dauernder Vorgänge anzeigen.

## Downloads

Für jede mit einem `v*`-Tag veröffentlichte Version erstellt GitHub Actions eigenständige Pakete für Windows, Linux und macOS. Laden Sie das Paket für Ihr System im Bereich **Assets** der jeweiligen [GitHub-Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) herunter; Python muss nicht installiert sein.

Die Anwendungsversion wird im Fenstertitel angezeigt. Das Anwendungssymbol ist in der Windows-EXE und im macOS-App-Bundle enthalten und wird auch im Anwendungsfenster, im Ladefenster und in der Taskleiste verwendet.

Beim ersten Start unter macOS ist möglicherweise eine Freigabe unter **Systemeinstellungen → Datenschutz & Sicherheit** erforderlich, da die Anwendung weder signiert noch notarisiert ist. Linux-Pakete sind für die im Paketnamen angegebene Architektur vorgesehen und benötigen einen grafischen Desktop mit Tk-Unterstützung.

## Versionierung und Releases

`pdf_manager_version.py` ist die einzige Quelle für die in der Anwendung angezeigte Version. Ändern Sie für eine Veröffentlichung dort `__version__` und erstellen und übertragen Sie anschließend einen passenden Git-Tag mit dem Präfix `v`. Beispiel für Version `1.0.0`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Der gleiche Workflow kann manuell über den Tab **Actions** des Repositorys gestartet werden; die erstellten Pakete stehen dann als Workflow-Artefakte zur Verfügung.

## Aus dem Quellcode starten

Installieren Sie Python 3.10 oder höher und die Abhängigkeiten und starten Sie anschließend die Anwendung:

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

So führen Sie die Tests aus:

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## Projektstruktur

- `pdf_manager.py`: Einstiegspunkt der Anwendung und Steuerung des Hauptfensters.
- `pdf_manager_ui/`: UI-Funktionen für Zusammenführen, Teilen, Komprimieren und Vorschau.
- `assets/icons/`: Quelldateien der Anwendungssymbole.
- `scripts/`: eigenständige Skripte zum Erstellen und Verpacken von Releases.
- `tests/`: Tests der Anwendung und des PDF-Dienstes.
- `pdf_manager_version.py`: in der Anwendung angezeigte Version.
