# GaLlaKk 的 PDF Manager

一款使用 Python 编写的桌面应用，可合并、拆分、压缩、旋转 PDF，并重新排列 PDF 页面。应用在本地运行：管理 PDF 时无需将私人文档上传或分享给在线服务。

## 阅读其他语言版本

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## 功能

- 将多个 PDF 合并为一个文档。
- 将 PDF 拆分为单独的页面。
- 以无损或均衡模式压缩 PDF。
- 保存前旋转并重新排列页面。
- 显示耗时操作的进度。

## 下载

每个使用 `v*` 标签发布的版本，GitHub Actions 都会为 Windows、Linux 和 macOS 构建独立运行包。请在对应 [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) 页面中的 **Assets** 区域下载适用于您系统的安装包；无需安装 Python。

应用版本显示在窗口标题中。应用图标包含在 Windows 可执行文件和 macOS 应用包中，也用于应用窗口、加载对话框和任务栏。

在 macOS 上，首次启动时可能需要在**系统设置 → 隐私与安全性**中批准，因为应用尚未签名或公证。Linux 安装包适用于包名中标明的处理器架构，并需要支持 Tk 的图形桌面环境。

## 版本管理与发布

`pdf_manager_version.py` 是应用显示版本的唯一来源。发布新版本时，请更新该文件中的 `__version__`，然后创建并推送对应的、以 `v` 开头的 Git 标签。例如，发布 `1.0.0`：

```bash
git tag v1.0.0
git push origin v1.0.0
```

也可以在仓库的 **Actions** 选项卡中手动启动相同的工作流；生成的安装包可作为工作流制品下载。

## 从源代码运行

安装 Python 3.10 或更高版本及应用依赖，然后启动应用：

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

运行测试：

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## 项目结构

- `pdf_manager.py`：应用入口和主窗口调度。
- `pdf_manager_ui/`：按合并、拆分、压缩和预览功能组织的界面代码。
- `assets/icons/`：应用图标源文件。
- `scripts/`：独立的构建和发布打包脚本。
- `tests/`：应用和 PDF 服务测试。
- `pdf_manager_version.py`：应用显示的版本。
