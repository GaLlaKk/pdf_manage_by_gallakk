# PDF Manager por GaLlaKk

Uma aplicação de desktop em Python para juntar, dividir, comprimir, rodar e reordenar páginas de PDF. A aplicação funciona localmente: pode gerir os seus PDFs sem carregar nem partilhar documentos privados com um serviço online.

## Ler noutro idioma

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## Funcionalidades

- Juntar vários PDFs num único documento.
- Dividir um PDF em páginas individuais.
- Comprimir PDFs nos modos sem perda ou equilibrado.
- Rodar e reordenar páginas antes de guardar.
- Mostrar o progresso de operações demoradas.

## Transferências

Para cada versão publicada com uma etiqueta `v*`, o GitHub Actions cria pacotes autónomos para Windows, Linux e macOS. Transfira o pacote para o seu sistema na secção **Assets** da página correspondente de [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases); não é necessário instalar o Python.

A versão da aplicação é apresentada no título da janela. O ícone está incluído no executável do Windows e no pacote da aplicação para macOS; também é utilizado na janela da aplicação, na caixa de diálogo de carregamento e na barra de tarefas.

No macOS, a primeira execução poderá exigir autorização em **Definições do Sistema → Privacidade e Segurança**, pois a aplicação não está assinada nem notarizada. Os pacotes Linux destinam-se à arquitetura indicada no nome do pacote e requerem um ambiente de trabalho gráfico com suporte para Tk.

## Versionamento e lançamentos

`pdf_manager_version.py` é a única fonte da versão apresentada pela aplicação. Para publicar uma versão, atualize `__version__` nesse ficheiro e crie e envie uma etiqueta Git correspondente com o prefixo `v`. Por exemplo, para a versão `1.0.0`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

O mesmo workflow pode ser iniciado manualmente no separador **Actions** do repositório; os pacotes criados ficam disponíveis como artefactos do workflow.

## Executar a partir do código-fonte

Instale o Python 3.10 ou posterior e as dependências da aplicação e, em seguida, inicie-a:

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

Para executar os testes:

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## Estrutura do projeto

- `pdf_manager.py`: ponto de entrada da aplicação e coordenação da janela principal.
- `pdf_manager_ui/`: interface agrupada pelas funções de junção, divisão, compressão e pré-visualização.
- `assets/icons/`: ficheiros-fonte dos ícones da aplicação.
- `scripts/`: scripts autónomos para compilação e criação de pacotes de lançamento.
- `tests/`: testes da aplicação e do serviço PDF.
- `pdf_manager_version.py`: versão apresentada pela aplicação.
