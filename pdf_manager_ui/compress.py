import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pdf_manager_service import compress_pdf



class CompressionTabMixin:
    """Compression tab application behavior."""

    def build_compress_tab(self):
        """Build the PDF compression tab and its quality options.

        Crée l'onglet de compression PDF et ses options de qualité.
        """
        self.compress_title_label = tk.Label(
            self.compress_tab,
            text=self.t("compress_title"),
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=15,
            pady=12,
        )
        self.compress_title_label.pack(fill="x")

        input_frame = tk.Frame(self.compress_tab, padx=15, pady=5)
        input_frame.pack(fill="x")
        self.compress_input_label = tk.Label(input_frame, text=self.t("compress_input_label"), width=16, anchor="w")
        self.compress_input_label.pack(side="left")
        self.compress_source_entry = tk.Entry(input_frame, textvariable=self.compress_source_var, width=60)
        self.compress_source_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.compress_choose_file_button = ttk.Button(
            input_frame,
            text=self.t("browse"),
            command=self.choose_compress_source,
        )
        self.compress_choose_file_button.pack(side="left")

        output_frame = tk.Frame(self.compress_tab, padx=15, pady=5)
        output_frame.pack(fill="x")
        self.compress_output_label = tk.Label(output_frame, text=self.t("compress_output_label"), width=16, anchor="w")
        self.compress_output_label.pack(side="left")
        self.compress_output_entry = tk.Entry(output_frame, textvariable=self.compress_output_var, width=60)
        self.compress_output_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.compress_choose_output_button = ttk.Button(
            output_frame,
            text=self.t("choose"),
            command=self.choose_compress_output,
        )
        self.compress_choose_output_button.pack(side="left")

        self.compress_mode_label = tk.Label(
            self.compress_tab,
            text=self.t("compress_mode_label"),
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=15,
            pady=10,
        )
        self.compress_mode_label.pack(fill="x")
        mode_frame = tk.Frame(self.compress_tab, padx=15)
        mode_frame.pack(fill="x")
        self.compress_lossless_radio = tk.Radiobutton(
            mode_frame,
            text=self.t("compress_lossless"),
            variable=self.compress_mode_var,
            value="lossless",
        )
        self.compress_lossless_radio.pack(anchor="w")
        self.compress_balanced_radio = tk.Radiobutton(
            mode_frame,
            text=self.t("compress_balanced"),
            variable=self.compress_mode_var,
            value="balanced",
        )
        self.compress_balanced_radio.pack(anchor="w")

        self.compress_info_label = tk.Label(
            self.compress_tab,
            text=self.t("compress_info"),
            justify="left",
            wraplength=760,
            fg="#444444",
            padx=15,
            pady=12,
            anchor="w",
        )
        self.compress_info_label.pack(fill="x")

        buttons_frame = tk.Frame(self.compress_tab, padx=15, pady=10)
        buttons_frame.pack(fill="x")
        self.compress_button = tk.Button(
            buttons_frame,
            text=self.t("compress_button"),
            command=self.compress_selected_pdf,
            width=18,
        )
        self.compress_button.pack(side="right")

    def choose_compress_source(self):
        """Select the PDF to compress and suggest a separate output path.

        Sélectionne le PDF à compresser et propose un chemin de sortie distinct.
        """
        file_path = filedialog.askopenfilename(
            title=self.t("compress_choose_file"),
            filetypes=[(self.t("files_filter"), "*.pdf"), (self.t("all_files"), "*.*")],
        )
        if file_path:
            def source_loaded(_page_count):
                self.compress_source_var.set(file_path)
                base_name, extension = os.path.splitext(file_path)
                self.compress_output_var.set(f"{base_name}_compressed{extension}")

            self.run_with_loading(
                self.t("compress_button"),
                lambda: self.read_pdf_page_count(file_path),
                source_loaded,
                lambda error: messagebox.showerror(
                    self.t("app_error"),
                    self.t("compress_fail", error=error),
                ),
            )

    def choose_compress_output(self):
        """Choose where to save the compressed PDF.

        Choisit l'emplacement d'enregistrement du PDF compressé.
        """
        source_path = self.compress_source_var.get().strip()
        initial_dir = os.path.dirname(source_path) if source_path else os.getcwd()
        default_name = os.path.basename(self.compress_output_var.get().strip()) or "compressed.pdf"
        output_path = filedialog.asksaveasfilename(
            title=self.t("compress_save_pdf"),
            initialdir=initial_dir,
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=[(self.t("files_filter"), "*.pdf")],
        )
        if output_path:
            self.compress_output_var.set(output_path)

    def compress_selected_pdf(self):
        """Compress the selected PDF and report file sizes or errors.

        Compresse le PDF sélectionné et affiche les tailles ou les erreurs.
        """
        source_path = self.compress_source_var.get().strip()
        if not source_path:
            messagebox.showwarning(self.t("no_selection"), self.t("compress_select_pdf"))
            return
        if not source_path.lower().endswith(".pdf") or not os.path.isfile(source_path):
            messagebox.showerror(self.t("invalid_pdf"), self.t("not_a_pdf"))
            return

        output_path = self.compress_output_var.get().strip()
        if not output_path:
            base_name, extension = os.path.splitext(source_path)
            output_path = f"{base_name}_compressed{extension}"
            self.compress_output_var.set(output_path)

        mode = self.compress_mode_var.get()

        def compress():
            compress_pdf(source_path, output_path, mode=mode)
            return os.path.getsize(source_path), os.path.getsize(output_path)

        def compression_complete(sizes):
            input_size, output_size = sizes
            messagebox.showinfo(
                self.t("compress_success"),
                self.t(
                    "compress_success_details",
                    input_size=f"{input_size:,}",
                    output_size=f"{output_size:,}",
                    path=output_path,
                ),
            )

        self.run_with_loading(
            self.t("compress_button"),
            compress,
            compression_complete,
            lambda error: messagebox.showerror(
                self.t("app_error"),
                self.t("compress_fail", error=error),
            ),
        )
