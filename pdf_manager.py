# ============================================================
# PDF merging and splitting - GaLlaKk
# Fusion et division de PDF - GaLlaKk
# PDF file management application using Tkinter
# Application de gestion de fichiers PDF avec Tkinter
# ============================================================

import locale
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk

import pymupdf
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD

from pdf_manager_version import __version__
from pdf_manager_ui.compress import CompressionTabMixin
from pdf_manager_ui.merge import MergeTabMixin
from pdf_manager_ui.preview import PreviewMixin
from pdf_manager_ui.split import SplitTabMixin

try:
    from ..pdf_manager_translations import LANG_ORDER, TRANSLATIONS
except ImportError:
    from pdf_manager_translations import LANG_ORDER, TRANSLATIONS

def detect_system_language():
    """Detect the interface language from the system locale.

    Détermine la langue de l'interface à partir des paramètres régionaux.
    """
    try:
        default_locale = locale.getlocale()[0] or ""
    except Exception:
        default_locale = ""

    if not default_locale:
        return "fr"

    short_code = default_locale.lower().replace("-", "_").split("_")[0]
    return short_code if short_code in TRANSLATIONS else "fr"

def resource_path(filename):
    """Return a path to a bundled resource or a source-tree asset."""
    bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(bundle_dir, filename)

class PdfManagerApp(MergeTabMixin, SplitTabMixin, CompressionTabMixin, PreviewMixin):
    """Main window for the PDF file management application.

    Fenêtre principale de l'application de gestion des fichiers PDF.
    """

    def __init__(self, root):
        """Initialize the window, tabs, and interface components.

        Initialise la fenêtre, ses onglets et les composants de l'interface.
        """
        self.root = root
        self._windows_icon_handles = []
        self.icon_path = resource_path("PDFManager.ico")
        if not os.path.isfile(self.icon_path):
            self.icon_path = resource_path(
                os.path.join("assets", "icons", "pdf_manager_logo_256x256.ico")
            )
        with Image.open(self.icon_path) as icon:
            largest_frame = max(
                range(getattr(icon, "n_frames", 1)),
                key=lambda frame: self.icon_frame_area(icon, frame),
            )
            icon.seek(largest_frame)
            self.app_icon = ImageTk.PhotoImage(icon.convert("RGBA"))
        self.root.iconphoto(True, self.app_icon)
        if os.name == "nt":
            self.root.iconbitmap(self.icon_path)
            self.root.iconbitmap(default=self.icon_path)
        self.current_lang = detect_system_language()
        self.translations = TRANSLATIONS
        self.root.title(self.window_title())
        self.root.geometry("1030x560")
        self.root.minsize(860, 430)
        if os.name == "nt":
            self._set_windows_icon(self.root)

        self.selected_files = []
        self.page_rotations = {}
        self.current_index = 0
        self.preview_page_index = 0
        self._busy = False
        self._closing = False
        self.loading_window = None
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        self.language_frame = tk.Frame(root, padx=10)
        self.language_frame.pack(fill="x", pady=(8, 0))
        self.language_label = tk.Label(self.language_frame, text=self.t("language"), anchor="e")
        language_values = [self.translations[code]["label"] for code in LANG_ORDER]
        self.language_var = tk.StringVar(value=self.translations[self.current_lang]["label"])
        self.language_combo = ttk.Combobox(
            self.language_frame,
            textvariable=self.language_var,
            values=language_values,
            state="readonly",
            width=14,
        )
        self.language_combo.pack(side="right", padx=(0, 10))
        self.language_label.pack(side="right", padx=(0, 5))
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        self.split_source_var = tk.StringVar(value="")
        self.split_output_dir_var = tk.StringVar(value="")
        self.compress_source_var = tk.StringVar(value="")
        self.compress_output_var = tk.StringVar(value="")
        self.compress_mode_var = tk.StringVar(value="lossless")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.merge_tab = tk.Frame(self.notebook, padx=10, pady=10)
        self.split_tab = tk.Frame(self.notebook, padx=10, pady=10)
        self.compress_tab = tk.Frame(self.notebook, padx=10, pady=10)

        self.notebook.add(self.merge_tab, text=self.t("merge_tab"))
        self.notebook.add(self.split_tab, text=self.t("split_tab"))
        self.notebook.add(self.compress_tab, text=self.t("compress_tab"))

        self.build_merge_tab()
        self.build_split_tab()
        self.build_compress_tab()
        self.apply_language()

    @staticmethod
    def icon_frame_area(icon, frame):
        icon.seek(frame)
        return icon.width * icon.height

    def _set_windows_icon(self, window):
        import ctypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        load_image = user32.LoadImageW
        load_image.argtypes = [
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
        ]
        load_image.restype = ctypes.c_void_p

        if not self._windows_icon_handles:
            icons = [
                load_image(None, self.icon_path, 1, size, size, 0x0010)
                for size in (16, 32)
            ]
            if not all(icons):
                destroy_icon = user32.DestroyIcon
                destroy_icon.argtypes = [ctypes.c_void_p]
                for icon in icons:
                    if icon:
                        destroy_icon(icon)
                raise ctypes.WinError(ctypes.get_last_error())
            self._windows_icon_handles.extend(icons)
        icons = self._windows_icon_handles
        send_message = user32.SendMessageW
        send_message.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_size_t,
            ctypes.c_void_p,
        ]
        send_message.restype = ctypes.c_ssize_t
        handle = window.winfo_id()
        for icon_type, icon in ((0, icons[0]), (1, icons[1]), (2, icons[0])):
            send_message(handle, 0x0080, icon_type, icon)

    def t(self, key, **kwargs):
        """Return translated text for the active language, formatted with parameters.

        Renvoie le texte traduit pour la langue active, avec ses paramètres.
        """
        text = self.translations.get(self.current_lang, self.translations["fr"]).get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def window_title(self):
        return f"{self.t('app_title')} v{__version__}"

    def close_application(self):
        """Close the application and clean up the current preview image."""
        self._closing = True
        if self.preview_temp_path and os.path.exists(self.preview_temp_path):
            os.remove(self.preview_temp_path)
        self.root.destroy()

    def run_with_loading(self, action, task, on_success, on_error):
        """Run a background task while displaying a modal loading window."""
        if self._busy:
            return

        self._busy = True
        window = tk.Toplevel(self.root)
        self.loading_window = window
        window.iconphoto(True, self.app_icon)
        if os.name == "nt":
            window.iconbitmap(self.icon_path)
        window.title(self.window_title())
        window.transient(self.root)
        window.resizable(False, False)
        window.protocol("WM_DELETE_WINDOW", lambda: None)

        frame = ttk.Frame(window, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=self.t("loading_message", action=action)).pack(pady=(0, 12))
        progress = ttk.Progressbar(frame, mode="indeterminate", length=280)
        progress.pack(fill="x")
        progress.start(12)

        window.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - window.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - window.winfo_height()) // 2
        window.geometry(f"+{x}+{y}")
        if os.name == "nt":
            self._set_windows_icon(window)
        window.grab_set()

        def finish(result=None, error=None):
            progress.stop()
            if window.winfo_exists():
                if window.grab_current() == window:
                    window.grab_release()
                window.destroy()
            self.loading_window = None
            self._busy = False
            if error is not None:
                on_error(error)
            else:
                on_success(result)

        def execute():
            try:
                result = task()
            except Exception as error:
                if self._closing:
                    return
                try:
                    self.root.after(0, lambda error=error: finish(error=error))
                except tk.TclError:
                    return
            else:
                if self._closing:
                    return
                try:
                    self.root.after(0, lambda result=result: finish(result=result))
                except tk.TclError:
                    return

        self.root.after(100, lambda: threading.Thread(target=execute, daemon=True).start())

    def read_pdf_page_count(self, pdf_path):
        """Read the page count for a selected PDF."""
        with pymupdf.open(pdf_path) as document:
            return document.page_count

    def on_language_change(self, event=None):
        """Apply the language selected in the drop-down list.

        Applique la langue choisie dans la liste déroulante.
        """
        selected_label = self.language_combo.get()
        selected_lang = next((code for code in LANG_ORDER if self.translations[code]["label"] == selected_label), self.current_lang)
        if selected_lang != self.current_lang:
            self.current_lang = selected_lang
            self.apply_language()

    def apply_language(self):
        """Refresh visible text after a language change.

        Actualise les textes visibles après un changement de langue.
        """
        self.root.title(self.window_title())
        self.language_label.config(text=self.t("language"))
        self.notebook.tab(0, text=self.t("merge_tab"))
        self.notebook.tab(1, text=self.t("split_tab"))
        self.notebook.tab(2, text=self.t("compress_tab"))

        self.merge_title_label.config(text=self.t("merge_title"))
        self.signature_label.config(text=self.t("signature"))
        self.open_button.config(text=self.t("open_pdf"))
        self.folder_button.config(text=self.t("add_folder"))
        self.remove_button.config(text=self.t("remove_selection"))
        self.up_button.config(text=self.t("move_up"))
        self.down_button.config(text=self.t("move_down"))
        self.preview_title_label.config(text=self.t("preview_title"))
        self.rotate_left_button.config(text=self.t("rotate_left"))
        self.rotate_right_button.config(text=self.t("rotate_right"))
        self.save_rotated_button.config(text=self.t("save_rotated"))
        self.output_label.config(text=self.t("output_file_label"))
        self.choose_output_button.config(text=self.t("choose"))
        self.merge_button.config(text=self.t("merge"))

        self.split_title_label.config(text=self.t("split_title"))
        self.pdf_file_label.config(text=self.t("pdf_file_label"))
        self.browse_source_button.config(text=self.t("browse"))
        self.output_dir_label.config(text=self.t("output_dir_label"))
        self.choose_output_dir_button.config(text=self.t("choose"))
        self.split_info_label.config(text=self.t("split_help"))
        self.split_button.config(text=self.t("split_button"))
        self.split_status_var.set(self.t("status_no_pdf"))

        self.compress_title_label.config(text=self.t("compress_title"))
        self.compress_input_label.config(text=self.t("compress_input_label"))
        self.compress_choose_file_button.config(text=self.t("browse"))
        self.compress_output_label.config(text=self.t("compress_output_label"))
        self.compress_choose_output_button.config(text=self.t("choose"))
        self.compress_mode_label.config(text=self.t("compress_mode_label"))
        self.compress_lossless_radio.config(text=self.t("compress_lossless"))
        self.compress_balanced_radio.config(text=self.t("compress_balanced"))
        self.compress_info_label.config(text=self.t("compress_info"))
        self.compress_button.config(text=self.t("compress_button"))

        self.update_preview()

if __name__ == "__main__":
    if os.name == "nt":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GaLlaKk.PDFManager")
    root = TkinterDnD.Tk()
    app = PdfManagerApp(root)
    root.mainloop()
