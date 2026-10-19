# PDF Manager de GaLlaKk

Una aplicación de escritorio en Python para combinar, dividir, comprimir, rotar y reordenar páginas PDF. La aplicación funciona localmente: puedes gestionar tus PDF sin subir ni compartir documentos privados con un servicio en línea.

## Leer en otro idioma

[English](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Português](README.pt.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [العربية](README.ar.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md)

## Funciones

- Combinar varios PDF en un solo documento.
- Dividir un PDF en páginas individuales.
- Comprimir PDF en modo sin pérdida o equilibrado.
- Rotar y reordenar páginas antes de guardar.
- Mostrar el progreso de las operaciones que tardan más.

## Descargas

Para cada versión publicada con una etiqueta `v*`, GitHub Actions crea paquetes independientes para Windows, Linux y macOS. Descarga el paquete para tu sistema en la sección **Assets** de la página de [GitHub Releases](https://github.com/GaLlaKk/pdf_manage_by_gallakk/releases) correspondiente; no es necesario instalar Python.

La versión de la aplicación aparece en el título de la ventana. El icono está incluido en el ejecutable de Windows y en el paquete de la app para macOS; también se utiliza en la ventana de la aplicación, el diálogo de carga y la barra de tareas.

En macOS, es posible que el primer inicio requiera autorización en **Ajustes del Sistema → Privacidad y seguridad**, porque la aplicación no está firmada ni notarizada. Los paquetes de Linux están destinados a la arquitectura indicada en el nombre del paquete y requieren un escritorio gráfico con compatibilidad con Tk.

## Versiones y publicaciones

`pdf_manager_version.py` es la única fuente de la versión que muestra la aplicación. Para publicar una versión, actualiza allí `__version__` y crea y sube una etiqueta de Git coincidente con el prefijo `v`. Por ejemplo, para la versión `1.0.0`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

También puedes iniciar el mismo workflow manualmente desde la pestaña **Actions** del repositorio; esos paquetes estarán disponibles como artefactos del workflow.

## Ejecutar desde el código fuente

Instala Python 3.10 o posterior y las dependencias de la aplicación; después, ejecútala:

```bash
python -m pip install -r requirements.txt
python pdf_manager.py
```

Para ejecutar las pruebas:

```bash
python -m pip install -r requirements-build.txt
python -m pytest -q
```

## Estructura del proyecto

- `pdf_manager.py`: punto de entrada de la aplicación y coordinación de la ventana principal.
- `pdf_manager_ui/`: interfaz organizada por funciones de combinación, división, compresión y vista previa.
- `assets/icons/`: archivos de origen de los iconos de la aplicación.
- `scripts/`: scripts independientes para compilar y empaquetar publicaciones.
- `tests/`: pruebas de la aplicación y del servicio PDF.
- `pdf_manager_version.py`: versión que muestra la aplicación.
