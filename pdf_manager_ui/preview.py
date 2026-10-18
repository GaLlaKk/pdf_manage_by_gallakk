import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

import pymupdf

from pdf_manager_service import rotate_pdf_pages



class PreviewMixin:
    """Preview application behavior."""

    def get_pdf_page_count(self, pdf_path):
        """Return the PDF page count, or zero if the file is inaccessible.

        Renvoie le nombre de pages du PDF, ou zéro s'il est inaccessible.
        """
        if not pdf_path or not os.path.isfile(pdf_path):
            return 0
        try:
            with pymupdf.open(pdf_path) as doc:
                return doc.page_count
        except Exception:
            return 0

    def rotate_current_page(self, degrees):
        """Rotate the page currently shown in the preview."""
        if not self.selected_files:
            return

        pdf_path = self.selected_files[self.current_index]
        rotations = self.page_rotations.setdefault(pdf_path, {})
        page_rotation = (rotations.get(self.preview_page_index, 0) + degrees) % 360
        if page_rotation:
            rotations[self.preview_page_index] = page_rotation
        else:
            del rotations[self.preview_page_index]
        if not rotations:
            del self.page_rotations[pdf_path]

        self.refresh_rotation_controls()
        self.update_preview()

    def refresh_rotation_controls(self, has_page=True):
        """Enable rotation and save controls for the current file."""
        state = tk.NORMAL if self.selected_files and has_page else tk.DISABLED
        self.rotate_left_button.config(state=state)
        self.rotate_right_button.config(state=state)
        has_rotations = bool(
            self.selected_files
            and self.page_rotations.get(self.selected_files[self.current_index])
        )
        self.save_rotated_button.config(state=tk.NORMAL if has_rotations else tk.DISABLED)

    def save_rotated_copy(self):
        """Save a separate copy of the selected PDF with its preview rotations."""
        if not self.selected_files:
            return
        pdf_path = self.selected_files[self.current_index]
        rotations = dict(self.page_rotations.get(pdf_path, {}))
        if not rotations:
            return

        base_name, extension = os.path.splitext(os.path.basename(pdf_path))
        output_path = filedialog.asksaveasfilename(
            title=self.t("save_rotated_dialog"),
            initialdir=os.path.dirname(pdf_path),
            initialfile=f"{base_name}_rotated{extension}",
            defaultextension=".pdf",
            filetypes=[(self.t("files_filter"), "*.pdf")],
        )
        if not output_path:
            return

        self.run_with_loading(
            self.t("save_rotated"),
            lambda: rotate_pdf_pages(pdf_path, output_path, rotations),
            lambda saved_path: messagebox.showinfo(
                self.t("rotated_success"),
                self.t("rotated_success_details", path=saved_path),
            ),
            lambda error: messagebox.showerror(
                self.t("app_error"),
                self.t("rotated_fail", error=error),
            ),
        )

    def render_pdf_thumbnail(self, pdf_path, page_number=0):
        """Render a PDF thumbnail in a worker thread."""
        with pymupdf.open(pdf_path) as document:
            page_count = document.page_count
            if page_count == 0:
                return page_count, None
            page_index = max(0, min(int(page_number), page_count - 1))
            page = document[page_index]
            page_rotation = self.page_rotations.get(pdf_path, {}).get(page_index, 0)
            page.set_rotation((page.rotation + page_rotation) % 360)
            pix = page.get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8), alpha=False)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_path = temp_file.name
        try:
            pix.save(temp_path)
        except Exception:
            os.remove(temp_path)
            raise
        return page_count, temp_path

    def set_preview_unavailable(self, pdf_path):
        self.prev_page_button.config(state=tk.DISABLED)
        self.next_page_button.config(state=tk.DISABLED)
        self.refresh_rotation_controls(has_page=False)
        self.preview_label.config(
            text=self.t("preview_unavailable", name=os.path.basename(pdf_path)),
            image="",
        )
        self.preview_label.image = None
        if self.preview_temp_path and os.path.exists(self.preview_temp_path):
            os.remove(self.preview_temp_path)
        self.preview_temp_path = None

    def display_preview(self, result, pdf_path):
        page_count, preview_path = result
        if page_count <= 0:
            self.preview_page_index = 0
            self.preview_page_var.set(self.t("page_label", current=1, total=1))
            self.prev_page_button.config(state=tk.DISABLED)
            self.next_page_button.config(state=tk.DISABLED)
            self.refresh_rotation_controls(has_page=False)
            self.set_preview_unavailable(pdf_path)
            return

        if self.preview_page_index >= page_count:
            self.preview_page_index = page_count - 1

        self.refresh_rotation_controls()
        self.preview_page_var.set(self.t("page_label", current=self.preview_page_index + 1, total=page_count))
        self.prev_page_button.config(
            state=tk.NORMAL if page_count > 1 and self.preview_page_index > 0 else tk.DISABLED
        )
        self.next_page_button.config(
            state=tk.NORMAL if page_count > 1 and self.preview_page_index < page_count - 1 else tk.DISABLED
        )

        if not preview_path:
            self.set_preview_unavailable(pdf_path)
            return

        old_preview_path = self.preview_temp_path
        try:
            photo = tk.PhotoImage(file=preview_path)
            max_width = 260
            max_height = 340
            width = photo.width()
            height = photo.height()
            scale = max(1, int(max(width / max_width, height / max_height)))
            if scale > 1:
                photo = photo.subsample(scale)
            self.preview_label.config(text="", image=photo, compound="center")
            self.preview_label.image = photo
            self.preview_temp_path = preview_path
        except (OSError, tk.TclError):
            self.set_preview_unavailable(pdf_path)
            if os.path.exists(preview_path):
                os.remove(preview_path)
            self.preview_temp_path = None

        if old_preview_path and os.path.exists(old_preview_path):
            os.remove(old_preview_path)

    def next_preview_page(self):
        """Go to the next page in the active PDF preview.

        Passe à la page suivante dans l'aperçu du PDF actif.
        """
        if not self.selected_files:
            return
        self.preview_page_index += 1
        self.update_preview()

    def previous_preview_page(self):
        """Go to the previous page in the active PDF preview.

        Revient à la page précédente dans l'aperçu du PDF actif.
        """
        if not self.selected_files:
            return
        if self.preview_page_index <= 0:
            return
        self.preview_page_index -= 1
        self.update_preview()

    def update_preview(self):
        """Refresh the preview image, page number, and navigation controls.

        Actualise l'image, le numéro de page et les commandes de navigation.
        """
        if not self.selected_files:
            if self.preview_temp_path and os.path.exists(self.preview_temp_path):
                os.remove(self.preview_temp_path)
            self.preview_temp_path = None
            self.preview_page_index = 0
            self.preview_page_var.set(self.t("page_label", current=1, total=1))
            self.prev_page_button.config(state=tk.DISABLED)
            self.next_page_button.config(state=tk.DISABLED)
            self.refresh_rotation_controls(has_page=False)
            self.preview_label.config(text=self.t("no_pdf_selected_preview"), image="")
            self.preview_label.image = None
            return

        if self.current_index >= len(self.selected_files):
            self.current_index = len(self.selected_files) - 1

        current_path = self.selected_files[self.current_index]
        page_index = self.preview_page_index
        self.preview_label.config(text=self.t("loading_message", action=self.t("preview_title")), image="")
        self.preview_label.image = None

        self.run_with_loading(
            self.t("preview_title"),
            lambda: self.render_pdf_thumbnail(current_path, page_index),
            lambda result: self.display_preview(result, current_path),
            lambda _error: self.set_preview_unavailable(current_path),
        )
