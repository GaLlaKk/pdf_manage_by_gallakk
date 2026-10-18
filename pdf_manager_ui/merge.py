import os
import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES

from pdf_manager_service import merge_pdfs



class MergeTabMixin:
    """Merge tab application behavior."""

    def build_merge_tab(self):
        """Build the merge tab controls, file list, and preview.

        Crée les commandes, la liste de fichiers et l'aperçu de fusion.
        """
        self.merge_title_label = tk.Label(
            self.merge_tab,
            text=self.t("merge_title"),
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=10,
        )
        self.merge_title_label.pack(fill="x")

        self.signature_label = tk.Label(
            self.merge_tab,
            text=self.t("signature"),
            font=("Segoe UI", 8),
            fg="#666666",
            anchor="e",
            padx=15,
            pady=5,
        )
        self.signature_label.pack(fill="x")

        frame_actions = tk.Frame(self.merge_tab, padx=15, pady=5)
        frame_actions.pack(fill="x")

        self.open_button = tk.Button(frame_actions, text=self.t("open_pdf"), command=self.select_files, width=18, state=tk.NORMAL)
        self.open_button.pack(side="left")

        self.folder_button = tk.Button(frame_actions, text=self.t("add_folder"), command=self.select_folder, width=18, state=tk.NORMAL)
        self.folder_button.pack(side="left", padx=10)

        self.remove_button = tk.Button(frame_actions, text=self.t("remove_selection"), command=self.remove_selected, width=18, state=tk.NORMAL)
        self.remove_button.pack(side="left")

        self.up_button = tk.Button(frame_actions, text=self.t("move_up"), command=self.move_up, width=10, state=tk.DISABLED)
        self.up_button.pack(side="left", padx=10)

        self.down_button = tk.Button(frame_actions, text=self.t("move_down"), command=self.move_down, width=10, state=tk.DISABLED)
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

        self.preview_title_label = tk.Label(right_frame, text=self.t("preview_title"), font=("Segoe UI", 10, "bold"), anchor="w")
        self.preview_title_label.pack(fill="x", pady=6)

        self.preview_nav = tk.Frame(right_frame)
        self.preview_nav.pack(fill="x", pady=6)

        self.prev_page_button = tk.Button(self.preview_nav, text="←", width=5, command=self.previous_preview_page, state=tk.DISABLED)
        self.prev_page_button.pack(side="left")

        self.preview_page_var = tk.StringVar(value=self.t("page_label", current=1, total=1))
        self.preview_page_label = tk.Label(self.preview_nav, textvariable=self.preview_page_var, font=("Segoe UI", 9), anchor="center")
        self.preview_page_label.pack(side="left", expand=True, fill="x")

        self.next_page_button = tk.Button(self.preview_nav, text="→", width=5, command=self.next_preview_page, state=tk.DISABLED)
        self.next_page_button.pack(side="right")

        rotation_frame = tk.Frame(right_frame)
        rotation_frame.pack(fill="x", pady=(0, 6))
        self.rotate_left_button = tk.Button(
            rotation_frame,
            text=self.t("rotate_left"),
            command=lambda: self.rotate_current_page(-90),
            state=tk.DISABLED,
        )
        self.rotate_left_button.pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.rotate_right_button = tk.Button(
            rotation_frame,
            text=self.t("rotate_right"),
            command=lambda: self.rotate_current_page(90),
            state=tk.DISABLED,
        )
        self.rotate_right_button.pack(side="left", expand=True, fill="x", padx=(3, 0))
        self.save_rotated_button = tk.Button(
            right_frame,
            text=self.t("save_rotated"),
            command=self.save_rotated_copy,
            state=tk.DISABLED,
        )
        self.save_rotated_button.pack(fill="x", pady=(0, 6))

        self.preview_label = tk.Label(
            right_frame,
            text=self.t("no_pdf_selected_preview"),
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

        self.output_label = tk.Label(output_frame, text=self.t("output_file_label"), anchor="w", width=16)
        self.output_label.pack(side="left")
        self.output_var = tk.StringVar(value="")
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.choose_output_button = ttk.Button(output_frame, text=self.t("choose"), command=self.choose_output_file)
        self.choose_output_button.pack(side="left")

        buttons_frame = tk.Frame(self.merge_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")

        self.merge_button = tk.Button(buttons_frame, text=self.t("merge"), command=self.merge_selected_files, width=18, state=tk.DISABLED)
        self.merge_button.pack(side="right")

        self.refresh_list()

    def select_files(self):
        """Add PDFs selected in the file picker to the list.

        Ajoute à la liste les PDF choisis dans le sélecteur de fichiers.
        """
        files = filedialog.askopenfilenames(
            title=self.t("select_pdf_files"),
            filetypes=[(self.t("all_files"), "*.*"), (self.t("files_filter"), "*.pdf")],
        )
        if not files:
            return

        pdf_files = []
        for file_path in files:
            if file_path.lower().endswith(".pdf"):
                pdf_files.append(file_path)

        if not pdf_files:
            messagebox.showwarning(self.t("no_selection"), self.t("select_a_pdf"))
            return

        self.add_pdf_files(pdf_files)

    def select_folder(self):
        """Add PDFs found in the selected folder to the list.

        Ajoute à la liste les PDF trouvés dans le dossier choisi.
        """
        folder_path = filedialog.askdirectory(title=self.t("select_folder_title"))
        if not folder_path:
            return

        def find_pdfs():
            return [
                full_path
                for file_name in sorted(os.listdir(folder_path))
                if (full_path := os.path.join(folder_path, file_name)).lower().endswith(".pdf")
                and os.path.isfile(full_path)
            ]

        self.run_with_loading(
            self.t("add_folder"),
            find_pdfs,
            self.add_pdf_files,
            lambda error: messagebox.showerror(self.t("app_error"), str(error)),
        )

    def add_pdf_files(self, pdf_files):
        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)

    def clear_placeholder(self, event=None):
        """Clear the list placeholder before the first file is selected.

        Efface le texte indicatif de la liste avant la première sélection.
        """
        if self.selected_files:
            return
        self.file_listbox.delete(0, tk.END)

    def on_listbox_select(self, event=None):
        """Update the active file and preview after a selection.

        Met à jour le fichier actif et son aperçu après une sélection.
        """
        selected_indexes = self.file_listbox.curselection()
        if selected_indexes:
            self.current_index = selected_indexes[0]
        elif self.selected_files:
            self.current_index = 0
        self.preview_page_index = 0
        self.refresh_buttons()
        self.update_preview()

    def on_drop(self, event):
        """Add PDF files dropped into the merge area to the list.

        Ajoute à la liste les fichiers PDF déposés dans la zone de fusion.
        """
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
            messagebox.showwarning(self.t("pdf_required"), self.t("drop_pdf_only"))
            return ""

        for file_path in pdf_files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        self.refresh_list()
        self.file_listbox.selection_clear(0, tk.END)
        return ""

    def move_up(self):
        """Move the selected file up by one position.

        Déplace le fichier sélectionné d'une position vers le début.
        """
        if not self.selected_files or self.current_index <= 0:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], self.selected_files[index]
        self.current_index = index - 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def move_down(self):
        """Move the selected file down by one position.

        Déplace le fichier sélectionné d'une position vers la fin.
        """
        if not self.selected_files or self.current_index >= len(self.selected_files) - 1:
            return
        index = self.current_index
        self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], self.selected_files[index]
        self.current_index = index + 1
        self.refresh_list()
        self.file_listbox.selection_set(self.current_index)
        self.refresh_buttons()

    def remove_selected(self):
        """Remove the currently selected files from the list.

        Retire de la liste les fichiers actuellement sélectionnés.
        """
        selected_indexes = list(self.file_listbox.curselection())
        if not selected_indexes:
            return
        for index in sorted(selected_indexes, reverse=True):
            del self.selected_files[index]
        self.refresh_list()

    def refresh_buttons(self):
        """Update button states based on file selection and order.

        Actualise l'état des boutons selon la sélection et l'ordre des fichiers.
        """
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
        """Rebuild the displayed list and refresh controls and preview.

        Reconstruit la liste affichée et actualise les commandes et l'aperçu.
        """
        self.file_listbox.delete(0, tk.END)
        if not self.selected_files:
            self.file_listbox.insert(tk.END, self.t("drop_files_hint"))
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
        """Open the save dialog for the merged PDF.

        Ouvre le sélecteur du chemin de sortie du PDF fusionné.
        """
        default_name = "fusion.pdf"
        if self.selected_files:
            default_name = os.path.splitext(os.path.basename(self.selected_files[0]))[0] + "_fusion.pdf"

        output_path = filedialog.asksaveasfilename(
            title=self.t("save_merge"),
            defaultextension=".pdf",
            filetypes=[(self.t("files_filter"), "*.pdf")],
            initialfile=default_name,
        )

        if output_path:
            self.output_var.set(output_path)

    def merge_selected_files(self):
        """Merge the selected PDFs and report the result or any error.

        Fusionne les PDF sélectionnés et affiche le résultat ou l'erreur.
        """
        if not self.selected_files:
            messagebox.showwarning(self.t("no_selection"), self.t("select_a_pdf"))
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            output_path = os.path.join(
                os.path.dirname(self.selected_files[0]),
                "fusion.pdf",
            )

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        pdf_files = list(self.selected_files)
        page_rotations = {
            pdf_path: dict(rotations)
            for pdf_path, rotations in self.page_rotations.items()
        }

        def merge():
            merge_pdfs(pdf_files, output_path, page_rotations=page_rotations)

        def merge_complete(_result):
            messagebox.showinfo(
                self.t("success_merge"),
                self.t("merge_success_details", path=output_path),
            )

        self.run_with_loading(
            self.t("merge"),
            merge,
            merge_complete,
            lambda error: messagebox.showerror(
                self.t("app_error"),
                self.t("merge_fail", error=error),
            ),
        )
