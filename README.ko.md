# GaLlaKk의 PDF Manager

PDF 페이지를 병합, 분할, 압축, 회전하고 순서를 바꿀 수 있는 Python 데스크톱 애플리케이션입니다. 애플리케이션은 로컬에서 실행되므로 비공개 문서를 온라인 서비스에 업로드하거나 공유하지 않고 PDF를 관리할 수 있습니다.

## 다른 언어로 읽기

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## 기능

- 여러 PDF를 하나의 문서로 병합
- PDF를 개별 페이지로 분할
- 무손실 또는 균형 모드로 PDF 압축
- 저장하기 전에 페이지 회전 및 순서 변경
- 오래 걸리는 작업의 진행률 표시

## 다운로드

`v*` 태그로 게시되는 각 버전마다 GitHub Actions가 Windows, Linux 및 macOS용 독립 실행 패키지를 빌드합니다. 해당 [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) 페이지의 **Assets** 섹션에서 운영 체제에 맞는 패키지를 다운로드하세요. Python을 설치할 필요가 없습니다.

애플리케이션 버전은 창 제목에 표시됩니다. 앱 아이콘은 Windows 실행 파일 및 macOS 앱 번들에 포함되며, 애플리케이션 창, 로딩 대화 상자 및 작업 표시줄에도 사용됩니다.

macOS에서는 애플리케이션이 서명 및 공증되지 않았으므로 첫 실행 시 **시스템 설정 → 개인정보 보호 및 보안**에서 허용해야 할 수 있습니다. Linux 패키지는 패키지 이름에 표시된 아키텍처용이며 Tk를 지원하는 그래픽 데스크톱 환경이 필요합니다.

## 버전 관리 및 릴리스

`pdf_manager_version.py`는 애플리케이션에 표시되는 버전의 단일 기준입니다. 릴리스할 때 이 파일의 `__version__`을 업데이트한 다음, `v` 접두사가 붙은 해당 Git 태그를 만들고 푸시하세요. 버전 `1.0.0`의 예:

```bash
git tag v1.0.0
git push origin v1.0.0
```

저장소의 **Actions** 탭에서 같은 워크플로를 수동으로 시작할 수도 있으며, 이 빌드 결과는 워크플로 아티팩트로 제공됩니다.

## 소스 코드에서 실행

Python 3.10 이상과 애플리케이션 종속성을 설치한 다음 앱을 실행하세요.

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

테스트를 실행하려면:

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## 프로젝트 구성

- `pdf_manager.py`: 애플리케이션 진입점 및 기본 창 제어.
- `pdf_manager_ui/`: 병합, 분할, 압축 및 미리 보기 기능별 UI 코드.
- `assets/icons/`: 애플리케이션 아이콘 소스 파일.
- `scripts/`: 독립적인 빌드 및 릴리스 패키징 스크립트.
- `tests/`: 애플리케이션 및 PDF 서비스 테스트.
- `pdf_manager_version.py`: 앱에 표시되는 버전.
