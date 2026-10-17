# ============================================================
# Fusion et division de PDF - GaLlaKk
# Application de gestion de fichiers PDF via interface Tkinter
# ============================================================

import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import fitz
from tkinterdnd2 import DND_FILES, TkinterDnD

try:
    from .pdf_manager_service import merge_pdfs, split_pdf_pages
except ImportError:
    from pdf_manager_service import merge_pdfs, split_pdf_pages


class PdfManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Manager by GaLlaKk")
        self.root.geometry("1030x560")
        self.root.minsize(860, 430)

        self.selected_files = []
        self.current_index = 0
        self.preview_page_index = 0

        self.split_source_var = tk.StringVar(value="")
        self.split_output_dir_var = tk.StringVar(value="")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.merge_tab = tk.Frame(self.notebook, padx=10, pady=10)
        self.split_tab = tk.Frame(self.notebook, padx=10, pady=10)

        self.notebook.add(self.merge_tab, text="Fusionner")
        self.notebook.add(self.split_tab, text="Diviser")

        self.build_merge_tab()
        self.build_split_tab()

    def build_merge_tab(self):
        tk.Label(
            self.merge_tab,
            text="Sélectionnez les fichiers PDF à fusionner :",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=10,
        ).pack(fill="x")

        tk.Label(
            self.merge_tab,
            text="GaLlaKk",
            font=("Segoe UI", 8),
            fg="#666666",
            anchor="e",
            padx=15,
            pady=5,
        ).pack(fill="x")

        frame_actions = tk.Frame(self.merge_tab, padx=15, pady=5)
        frame_actions.pack(fill="x")

        self.open_button = tk.Button(frame_actions, text="Ouvrir PDF", command=self.select_files, width=18, state=tk.NORMAL)
        self.open_button.pack(side="left")

        self.folder_button = tk.Button(frame_actions, text="Ajouter un dossier", command=self.select_folder, width=18, state=tk.NORMAL)
        self.folder_button.pack(side="left", padx=10)

        self.remove_button = tk.Button(frame_actions, text="Retirer la sélection", command=self.remove_selected, width=18, state=tk.NORMAL)
        self.remove_button.pack(side="left")

        self.up_button = tk.Button(frame_actions, text="Monter", command=self.move_up, width=10, state=tk.DISABLED)
        self.up_button.pack(side="left", padx=10)

        self.down_button = tk.Button(frame_actions, text="Descendre", command=self.move_down, width=10, state=tk.DISABLED)
        self.down_button.pack(side="left")

        content_frame = tk.Frame(self.merge_tab, padx=15, pady=8)
        content_frame.pack(fill="both", expand=True)

        left_frame = tk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        self.file_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=14, font=("Segoe UI", 10))
        self.file_listbox.pack(fill="both", expand=True)
        self.file_listbox.config(bg="#f7f7f7")
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
        self.file_listbox.bind("<Button-1>", self.clear_placeholder)
        self.file_listbox.bind("<ButtonRelease-1>", self.on_listbox_select)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        right_frame = tk.Frame(content_frame, width=300, padx=10)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Aperçu du PDF", font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", pady=6)

        self.preview_nav = tk.Frame(right_frame)
        self.preview_nav.pack(fill="x", pady=6)

        self.prev_page_button = tk.Button(self.preview_nav, text="←", width=5, command=self.previous_preview_page, state=tk.DISABLED)
        self.prev_page_button.pack(side="left")

        self.preview_page_var = tk.StringVar(value="Page 1 / 1")
        self.preview_page_label = tk.Label(self.preview_nav, textvariable=self.preview_page_var, font=("Segoe UI", 9), anchor="center")
        self.preview_page_label.pack(side="left", expand=True, fill="x")

        self.next_page_button = tk.Button(self.preview_nav, text="→", width=5, command=self.next_preview_page, state=tk.DISABLED)
        self.next_page_button.pack(side="right")

        self.preview_label = tk.Label(
            right_frame,
            text="Aucun aperçu disponible",
            bg="#f5f5f5",
            relief="solid",
            bd=1,
            anchor="center",
            justify="center",
            compound="center",
            font=("Segoe UI", 9),
        )
        self.preview_label.pack(fill="both", expand=True)
        self.preview_label.image = None
        self.preview_temp_path = None

        output_frame = tk.Frame(self.merge_tab, padx=15, pady=5)
        output_frame.pack(fill="x")

        tk.Label(output_frame, text="Fichier de sortie :", anchor="w", width=16).pack(side="left")
        self.output_var = tk.StringVar(value="")
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=10)
        ttk.Button(output_frame, text="Choisir", command=self.choose_output_file).pack(side="left")

        buttons_frame = tk.Frame(self.merge_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")

        self.merge_button = tk.Button(buttons_frame, text="Fusionner", command=self.merge_selected_files, width=18, state=tk.DISABLED)
        self.merge_button.pack(side="right")

        self.refresh_list()

    def build_split_tab(self):
        tk.Label(
            self.split_tab,
            text="Sélectionnez un PDF à découper :",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=12,
        ).pack(fill="x")

        file_frame = tk.Frame(self.split_tab, padx=15, pady=5)
        file_frame.pack(fill="x")
        tk.Label(file_frame, text="Fichier PDF :", width=16, anchor="w").pack(side="left")
        self.split_source_entry = tk.Entry(file_frame, textvariable=self.split_source_var, width=60)
        self.split_source_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.split_source_entry.drop_target_register(DND_FILES)
        self.split_source_entry.dnd_bind('<<Drop>>', self.on_split_drop)
        ttk.Button(file_frame, text="Parcourir", command=self.choose_split_source).pack(side="left")

        output_dir_frame = tk.Frame(self.split_tab, padx=15, pady=5)
        output_dir_frame.pack(fill="x")
        tk.Label(output_dir_frame, text="Dossier de sortie :", width=16, anchor="w").pack(side="left")
        self.split_output_entry = tk.Entry(output_dir_frame, textvariable=self.split_output_dir_var, width=60)
        self.split_output_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.split_output_entry.drop_target_register(DND_FILES)
        self.split_output_entry.dnd_bind('<<Drop>>', self.on_split_output_drop)
        ttk.Button(output_dir_frame, text="Choisir", command=self.choose_split_output_dir).pack(side="left")

        info_frame = tk.Frame(self.split_tab, padx=15, pady=5)
        info_frame.pack(fill="x")
        tk.Label(
            info_frame,
            text="Le nom des fichiers générés sera de la forme : nomfichier_1.pdf, nomfichier_02.pdf, nomfichier_123.pdf selon le nombre total de pages.",
            justify="left",
            wraplength=700,
            fg="#444444",
        ).pack(anchor="w")

        buttons_frame = tk.Frame(self.split_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")
        self.split_button = tk.Button(buttons_frame, text="Diviser", command=self.split_selected_pdf, width=18)
        self.split_button.pack(side="right")

        self.split_status_var = tk.StringVar(value="Aucun PDF sélectionné.")
        tk.Label(self.split_tab, textvariable=self.split_status_var, fg="#333333", padx=15, pady=5, anchor="w").pack(fill="x")

    def choose_split_source(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner le PDF à découper",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
        )
        if file_path:
            self.split_source_var.set(file_path)
            self.split_status_var.set(f"PDF sélectionné : {os.path.basename(file_path)}")
            if not self.split_output_dir_var.get().strip():
                self.split_output_dir_var.set(os.path.dirname(file_path))

    def on_split_drop(self, event):
        try:
            paths = self.split_source_entry.tk.splitlist(event.data)
        except Exception:
            paths = []

        if not paths:
            return ""

        dropped_file = paths[0]
        if not dropped_file.lower().endswith(".pdf"):
            messagebox.showwarning("PDF requis", "Veuillez déposer un fichier PDF valide.")
            return ""

        self.split_source_var.set(dropped_file)
        self.split_status_var.set(f"PDF sélectionné : {os.path.basename(dropped_file)}")
        if not self.split_output_dir_var.get().strip():
            self.split_output_dir_var.set(os.path.dirname(dropped_file))
        return ""

    def choose_split_output_dir(self):
        directory = filedialog.askdirectory(title="Choisir le dossier de destination")
        if directory:
            self.split_output_dir_var.set(directory)

    def on_split_output_drop(self, event):
        try:
            paths = self.split_output_entry.tk.splitlist(event.data)
        except Exception:
            paths = []

        if not paths:
            return ""

        dropped_path = paths[0]
        if os.path.isdir(dropped_path):
            self.split_output_dir_var.set(dropped_path)
        else:
            self.split_output_dir_var.set(os.path.dirname(dropped_path))
        return ""

    def split_selected_pdf(self):
        pdf_path = self.split_source_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("Aucun PDF", "Veuillez sélectionner un fichier PDF à diviser.")
            return

        if not pdf_path.lower().endswith(".pdf"):
            messagebox.showerror("Fichier invalide", "Le fichier sélectionné n'est pas un PDF.")
            return

        output_dir = self.split_output_dir_var.get().strip()
        if not output_dir:
            output_dir = os.path.dirname(pdf_path)

        try:
            created_files = split_pdf_pages(pdf_path, output_dir=output_dir)
            self.split_status_var.set(f"{len(created_files)} fichiers générés dans : {output_dir}")
            messagebox.showinfo(
                "Découpage réussi",
                f"{len(created_files)} fichiers PDF individuels ont été créés dans :\n{output_dir}",
            )
        except Exception as exc:
            messagebox.showerror("Erreur", f"Le découpage a échoué :\n{exc}")

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers PDF",
            filetypes=[("Tous les fichiers", "*.*"), ("Fichiers PDF", "*.pdf")],
        )
        if not files:
            return

        pdf_files = []
        for file_path in files:
            if file_path.lower().endswith(".pdf"):
                pdf_files.append(file_path)

        if not pdf_files:
            messagebox.showwarning("Aucun PDF", "Veuillez sélectionner au moins un fichier PDF.")
            return

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier contenant des PDF")
        if not folder_path:
            return

        pdf_files = []
        for file_name in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, file_name)
            if os.path.isfile(full_path) and full_path.lower().endswith(".pdf"):
                pdf_files.append(full_path)

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)

    def clear_placeholder(self, event=None):
        if self.selected_files:
            return
        self.file_listbox.delete(0, tk.END)

    def on_listbox_select(self, event=None):
        selected_indexes = self.file_listbox.curselection()
        if selected_indexes:
            self.current_index = selected_indexes[0]
        elif self.selected_files:
            self.current_index = 0
        self.preview_page_index = 0
        self.refresh_buttons()
        self.update_preview()

    def get_pdf_page_count(self, pdf_path):
        if not pdf_path or not os.path.isfile(pdf_path):
            return 0
        try:
            with fitz.open(pdf_path) as doc:
                return doc.page_count
        except Exception:
            return 0

    def render_pdf_thumbnail(self, pdf_path, page_number=0):
        if not pdf_path or not os.path.isfile(pdf_path):
            return None

        try:
            with fitz.open(pdf_path) as doc:
                if doc.page_count == 0:
                    return None
                page_index = max(0, min(int(page_number), doc.page_count - 1))
                page = doc[page_index]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False)

                if self.preview_temp_path and os.path.exists(self.preview_temp_path):
                    os.remove(self.preview_temp_path)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_path = temp_file.name
                pix.save(temp_path)
                self.preview_temp_path = temp_path
                return temp_path
        except Exception:
            return None

    def next_preview_page(self):
        if not self.selected_files:
            return
        pdf_path = self.selected_files[self.current_index]
        page_count = self.get_pdf_page_count(pdf_path)
        if page_count <= 1:
            return
        self.preview_page_index = min(page_count - 1, self.preview_page_index + 1)
        self.update_preview()

    def previous_preview_page(self):
        if not self.selected_files:
            return
        if self.preview_page_index <= 0:
            return
        self.preview_page_index -= 1
        self.update_preview()

    def update_preview(self):
        if not self.selected_files:
            self.preview_page_index = 0
            self.preview_page_var.set("Page 1 / 1")
            self.prev_page_button.config(state=tk.DISABLED)
            self.next_page_button.config(state=tk.DISABLED)
            self.preview_label.config(text="Aucun PDF sélectionné\nAjoutez un fichier pour voir l'aperçu", image="")
            self.preview_label.image = None
            return

        if self.current_index >= len(self.selected_files):
            self.current_index = len(self.selected_files) - 1

        current_path = self.selected_files[self.current_index]
        page_count = self.get_pdf_page_count(current_path)
        if page_count <= 0:
            self.preview_page_index = 0
            self.preview_page_var.set("Page 1 / 1")
            self.prev_page_button.config(state=tk.DISABLED)
            self.next_page_button.config(state=tk.DISABLED)
            self.preview_label.config(text=f"Prévisualisation indisponible\n{os.path.basename(current_path)}", image="")
            self.preview_label.image = None
            return

        if self.preview_page_index >= page_count:
            self.preview_page_index = page_count - 1

        self.preview_page_var.set(f"Page {self.preview_page_index + 1} / {page_count}")
        self.prev_page_button.config(state=tk.NORMAL if page_count > 1 and self.preview_page_index > 0 else tk.DISABLED)
        self.next_page_button.config(state=tk.NORMAL if page_count > 1 and self.preview_page_index < page_count - 1 else tk.DISABLED)

        preview_path = self.render_pdf_thumbnail(current_path, self.preview_page_index)

        if not preview_path:
            self.preview_label.config(text=f"Prévisualisation indisponible\n{os.path.basename(current_path)}", image="")
            self.preview_label.image = None
            return

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
        except Exception:
            self.preview_label.config(text=f"Aperçu non disponible\n{os.path.basename(current_path)}", image="")
            self.preview_label.image = None

    def on_drop(self, event):
        file_paths = []
        try:
            file_paths = self.file_listbox.tk.splitlist(event.data)
        except Exception:
            file_paths = []

        pdf_files = []
        for file_path in file_paths:
            if file_path.lower().endswith(".pdf"):
                pdf_files.append(file_path)

        if not pdf_files:
            messagebox.showwarning("Aucun PDF", "Glissez uniquement des fichiers PDF.")
            return ""

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)
        return ""

    def move_up(self):
        if not self.selected_files or self.current_index <= 0:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], self.selected_files[index]
        self.current_index = index - 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def move_down(self):
        if not self.selected_files or self.current_index >= len(self.selected_files) - 1:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], self.selected_files[index]
        self.current_index = index + 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def remove_selected(self):
        selected_indexes = list(self.file_listbox.curselection())
        if not selected_indexes:
            return
        for index in sorted(selected_indexes, reverse=True):
            del self.selected_files[index]
        self.refresh_list()

    def refresh_buttons(self):
        has_files = bool(self.selected_files)
        self.merge_button.config(state=tk.NORMAL if has_files else tk.DISABLED)
        self.remove_button.config(state=tk.NORMAL if has_files else tk.DISABLED)

        if not has_files:
            self.up_button.config(state=tk.DISABLED)
            self.down_button.config(state=tk.DISABLED)
            return

        index = self.current_index if self.current_index < len(self.selected_files) else len(self.selected_files) - 1
        self.up_button.config(state=tk.NORMAL if index > 0 and len(self.selected_files) > 1 else tk.DISABLED)
        self.down_button.config(state=tk.NORMAL if index < len(self.selected_files) - 1 and len(self.selected_files) > 1 else tk.DISABLED)

    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        if not self.selected_files:
            self.file_listbox.insert(tk.END, "Glissez ici vos fichiers PDF")
            self.file_listbox.config(bg="#f7f7f7")
            self.file_listbox.selection_clear(0, tk.END)
            self.current_index = 0
        else:
            for file_path in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
            self.file_listbox.config(bg="white")
            if self.current_index >= len(self.selected_files):
                self.current_index = len(self.selected_files) - 1
            self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()
        self.update_preview()

    def choose_output_file(self):
        default_name = "fusion.pdf"
        if self.selected_files:
            default_name = os.path.splitext(os.path.basename(self.selected_files[0]))[0] + "_fusion.pdf"

        output_path = filedialog.asksaveasfilename(
            title="Enregistrer le PDF fusionné",
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf")],
            initialfile=default_name,
        )

        if output_path:
            self.output_var.set(output_path)

    def merge_selected_files(self):
        if not self.selected_files:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner au moins un fichier PDF.")
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            output_path = os.path.join(
                os.path.dirname(self.selected_files[0]),
                "fusion.pdf",
            )

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        try:
            merge_pdfs(self.selected_files, output_path)
            messagebox.showinfo(
                "Fusion réussie",
                f"Le fichier PDF a bien été créé :\n{output_path}",
            )
        except Exception as exc:
            messagebox.showerror("Erreur", f"La fusion a échoué :\n{exc}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PdfManagerApp(root)
    root.mainloop()
