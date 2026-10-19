# GaLlaKk の PDF Manager

PDF の結合、分割、圧縮、回転、ページの並べ替えができる Python 製デスクトップアプリケーションです。アプリはローカルで動作するため、オンラインサービスに PDF をアップロードしたり、個人の文書を共有したりせずに管理できます。

## 他の言語で読む

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## 機能

- 複数の PDF を 1 つの文書に結合。
- PDF をページ単位に分割。
- PDF をロスレスまたはバランスモードで圧縮。
- 保存前にページを回転・並べ替え。
- 時間のかかる処理の進行状況を表示。

## ダウンロード

`v*` タグでリリースされる各バージョンについて、GitHub Actions が Windows、Linux、macOS 向けのスタンドアロンパッケージをビルドします。[GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) の該当バージョンの **Assets** から、お使いのシステム用パッケージをダウンロードしてください。Python のインストールは不要です。

アプリのバージョンはウィンドウタイトルに表示されます。アプリのアイコンは Windows 実行ファイルと macOS アプリバンドルに含まれ、アプリのウィンドウ、読み込みダイアログ、タスクバーでも使用されます。

macOS では、アプリが署名・公証されていないため、初回起動時に**システム設定 → プライバシーとセキュリティ**で許可が必要になる場合があります。Linux パッケージはパッケージ名に記載されたアーキテクチャ向けで、Tk 対応のグラフィカルデスクトップ環境が必要です。

## バージョン管理とリリース

`pdf_manager_version.py` はアプリに表示されるバージョンの唯一の管理元です。リリース時は同ファイルの `__version__` を更新し、対応する `v` 付きの Git タグを作成して push します。バージョン `1.0.0` の例：

```bash
git tag v1.0.0
git push origin v1.0.0
```

同じワークフローはリポジトリの **Actions** タブから手動で実行することもできます。そのビルドはワークフローのアーティファクトとして利用できます。

## ソースから実行

Python 3.10 以降とアプリの依存関係をインストールしてから、アプリを起動します。

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

テストを実行するには：

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## プロジェクト構成

- `pdf_manager.py`：アプリのエントリーポイントとメインウィンドウの制御。
- `pdf_manager_ui/`：結合、分割、圧縮、プレビュー機能ごとに整理された UI。
- `assets/icons/`：アプリアイコンのソースファイル。
- `scripts/`：ビルドとリリース用パッケージ作成の独立したスクリプト。
- `tests/`：アプリと PDF サービスのテスト。
- `pdf_manager_version.py`：アプリに表示されるバージョン。
