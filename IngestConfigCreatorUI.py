"""Desktop UI (customtkinter) front-end for the Ingest Config Creator."""

import os
import queue
import sys
import threading
import traceback
import webbrowser

# the creator modules resolve imports and SourcePlugins relative to this folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
os.chdir(SCRIPT_DIR)

import customtkinter as ctk
from tkinter import filedialog, messagebox

from IngestConfigCreatorPrefect import ingestconfigcreator_prefect
from IngestConfigCreatorAud import ingestconfigcreator_aud
from version import version, releasedate

SOURCE_TYPES = ["KIP", "FF", "AUD"]
HELP_URL = "https://kraftanalyticsgroup.atlassian.net/wiki/x/vAC_6g"

# display label -> the source type code the creator modules expect
SOURCE_TYPE_LABELS = {"KIP": "API", "FF": "Flat File", "AUD": "RawAudience"}
SOURCE_TYPE_CODES = {label: code for code, label in SOURCE_TYPE_LABELS.items()}

SOURCE_TYPE_HELP = {
    "KIP": "Ingest resources for API / non flat file sources. Requires a data dictionary Excel file.",
    "FF": "Ingest resources for Flat File sources. Requires a data dictionary Excel file.",
    "AUD": "RawAudience config resources and test queries only. Requires a data dictionary Excel file.",
}

DEFAULT_FILEDATE_REGEX = {"KIP": "[0-9]{14}", "FF": "[0-9]{8,12}"}

ICP_KEYS = [
    "sourcetype",
    "client",
    "database",
    "sourcename",
    "copyffoptions",
    "filedateregex",
    "fileimportmatch",
    "delimiter",
    "enclosedby",
    "pgpkey",
]


class _QueueWriter:
    """stdout replacement that forwards only newly added text to a queue.

    Logger.log() reprints its whole accumulated buffer on every call, so each
    block is a superset of the previous one; only the delta is forwarded.
    """

    def __init__(self, log_queue: queue.Queue):
        self._queue = log_queue
        self._cumulative = ""

    def write(self, text):
        if not text or text.strip("\r\n") == "":
            return
        if text.startswith(self._cumulative) and len(text) > len(self._cumulative):
            delta = text[len(self._cumulative):]
            self._cumulative = text
        elif text == self._cumulative:
            return
        else:
            delta = text
        delta = delta.strip("\n")
        if delta:
            self._queue.put(delta)

    def flush(self):
        pass

    def isatty(self):
        return False


class IngestConfigCreatorUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"Ingest Config Creator {version}")
        self.geometry("980x820")
        self.minsize(820, 640)

        self._log_queue = queue.Queue()
        self._worker = None
        self._output_folder = ""

        self._label_font = ctk.CTkFont(size=13)
        self._title_font = ctk.CTkFont(size=20, weight="bold")
        self._mono_font = ctk.CTkFont(family="Consolas", size=12)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_form()
        self._build_actions()
        self._build_log()

        self._on_source_type_change(self._source_type.get())
        self.after(100, self._drain_log_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # layout
    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Ingest Config Creator", font=self._title_font).grid(
            row=0, column=0, columnspan=2, padx=(20, 0), pady=(12, 0), sticky="w"
        )
        ctk.CTkLabel(
            header,
            text=f"version {version}  -  released {releasedate}",
            font=self._label_font,
            text_color=("gray40", "gray60"),
        ).grid(row=1, column=0, padx=(20, 0), pady=(0, 12), sticky="w")

        help_link = ctk.CTkLabel(
            header,
            text="Help Documentation",
            text_color=("#1f6aa5", "#6aa9e0"),
            font=ctk.CTkFont(size=13, underline=True),
            cursor="hand2",
        )
        help_link.grid(row=1, column=1, padx=(20, 0), pady=(0, 14), sticky="w")
        help_link.bind("<Button-1>", lambda _event: webbrowser.open_new_tab(HELP_URL))

        ctk.CTkLabel(header, text="UI Theme", font=self._label_font).grid(
            row=0, column=2, padx=(0, 10), sticky="e"
        )
        ctk.CTkOptionMenu(
            header,
            width=150,
            values=["System", "Dark", "Light"],
            command=ctk.set_appearance_mode,
        ).grid(row=0, column=3, padx=(0, 16), sticky="e")

        self._profile_summary = ctk.CTkLabel(
            header, text="No profile loaded", font=self._label_font, text_color=("gray40", "gray60")
        )
        self._profile_summary.grid(row=1, column=2, padx=(0, 10), sticky="e")

        ctk.CTkButton(
            header, text="Load profile (.icp)", width=150, command=self._load_profile
        ).grid(row=1, column=3, padx=(0, 16), sticky="e")

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=16, pady=(12, 0), sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        # source type ---------------------------------------------------
        ctk.CTkLabel(form, text="Source type", font=self._label_font).grid(
            row=0, column=0, padx=(16, 8), pady=(16, 4), sticky="w"
        )
        self._source_type = ctk.StringVar(value="KIP")
        self._source_type_label = ctk.StringVar(value=SOURCE_TYPE_LABELS["KIP"])
        ctk.CTkSegmentedButton(
            form,
            values=[SOURCE_TYPE_LABELS[code] for code in SOURCE_TYPES],
            variable=self._source_type_label,
            command=self._on_source_label_change,
        ).grid(row=0, column=1, padx=8, pady=(16, 4), sticky="w")

        self._source_hint = ctk.CTkLabel(
            form, text="", font=self._label_font, text_color=("gray40", "gray60"), anchor="w"
        )
        self._source_hint.grid(row=1, column=1, columnspan=2, padx=8, pady=(0, 8), sticky="w")

        # fields --------------------------------------------------------
        self._entries = {}
        self._rows = {}
        row = 2

        row = self._add_row(form, row, "ddfile", "Data dictionary file *", browse="file")
        row = self._add_row(form, row, "client", "Client abbreviation *")
        row = self._add_row(form, row, "database", "Database name *")
        row = self._add_row(form, row, "sourcename", "Source name *")
        row = self._add_row(form, row, "delimiter", "Column delimiter *")
        row = self._add_row(form, row, "fileimportmatch", "File import match pattern *")
        row = self._add_row(form, row, "copyffoptions", "Copy Into file format options")
        row = self._add_row(form, row, "filedateregex", "File date regex")
        row = self._add_row(form, row, "enclosedby", 'Enclosing character (default ")')
        row = self._add_row(form, row, "pgpkey", "PGP key account")
        row = self._add_row(form, row, "reporootfolder", "Repo root folder", browse="folder")

        ctk.CTkLabel(
            form,
            text="* required.  Repo root folder is optional - leave blank to skip creating files in repo folders.",
            font=self._label_font,
            text_color=("gray40", "gray60"),
        ).grid(row=row, column=0, columnspan=3, padx=16, pady=(4, 16), sticky="w")

    def _add_row(self, parent, row, key, label, browse=None):
        widgets = []

        lbl = ctk.CTkLabel(parent, text=label, font=self._label_font, anchor="w")
        lbl.grid(row=row, column=0, padx=(16, 8), pady=5, sticky="w")
        widgets.append(lbl)

        entry = ctk.CTkEntry(parent, placeholder_text=label)
        span = 1 if browse else 2
        entry.grid(row=row, column=1, columnspan=span, padx=8, pady=5, sticky="ew")
        widgets.append(entry)
        self._entries[key] = entry

        if browse:
            cmd = self._browse_file if browse == "file" else self._browse_folder
            btn = ctk.CTkButton(parent, text="Browse", width=90, command=lambda k=key: cmd(k))
            btn.grid(row=row, column=2, padx=(8, 16), pady=5, sticky="e")
            widgets.append(btn)

        self._rows[key] = widgets
        return row + 1

    def _build_actions(self):
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, padx=16, pady=(12, 0), sticky="ew")
        actions.grid_columnconfigure(3, weight=1)

        self._run_button = ctk.CTkButton(actions, text="Create config", width=160, command=self._run)
        self._run_button.grid(row=0, column=0, padx=(0, 8))

        self._open_button = ctk.CTkButton(
            actions, text="Open output folder", width=160, state="disabled", command=self._open_output_folder
        )
        self._open_button.grid(row=0, column=1, padx=8)

        ctk.CTkButton(actions, text="Clear log", width=110, command=self._clear_log).grid(row=0, column=2, padx=8)

        self._progress = ctk.CTkProgressBar(actions, mode="indeterminate")
        self._progress.grid(row=0, column=3, padx=(16, 0), sticky="ew")
        self._progress.set(0)

    def _build_log(self):
        self._log = ctk.CTkTextbox(self, font=self._mono_font, wrap="word")
        self._log.grid(row=3, column=0, padx=16, pady=16, sticky="nsew")
        self._log.configure(state="disabled")

    # ------------------------------------------------------------------
    # behaviour
    # ------------------------------------------------------------------
    def _on_source_label_change(self, label):
        self._set_source_type(SOURCE_TYPE_CODES.get(label, "KIP"))

    def _set_source_type(self, source_type):
        self._source_type.set(source_type)
        self._source_type_label.set(SOURCE_TYPE_LABELS[source_type])
        self._on_source_type_change(source_type)

    def _on_source_type_change(self, source_type):
        self._source_hint.configure(text=SOURCE_TYPE_HELP.get(source_type, ""))

        prefect_only = ["copyffoptions", "filedateregex"]
        ff_only = ["delimiter", "enclosedby", "fileimportmatch", "pgpkey"]

        visible = set()
        if source_type in ("KIP", "FF"):
            visible.update(prefect_only)
        if source_type == "FF":
            visible.update(ff_only)

        for key in prefect_only + ff_only:
            for widget in self._rows[key]:
                if key in visible:
                    widget.grid()
                else:
                    widget.grid_remove()

        self._entries["filedateregex"].configure(
            placeholder_text=f"default {DEFAULT_FILEDATE_REGEX.get(source_type, '')}"
        )

    def _browse_file(self, key):
        path = filedialog.askopenfilename(
            title="Select Excel data dictionary file", filetypes=[("Excel", "*.xlsx"), ("All files", "*.*")]
        )
        if path:
            self._set_entry(key, os.path.normpath(path))

    def _browse_folder(self, key):
        path = filedialog.askdirectory(title="Select folder containing cloned repos")
        if path:
            self._set_entry(key, os.path.normpath(path) + os.sep)

    def _set_entry(self, key, value):
        entry = self._entries[key]
        entry.delete(0, "end")
        entry.insert(0, value or "")

    def _load_profile(self):
        path = filedialog.askopenfilename(
            title="Select config creator profile", filetypes=[("Ingest Config Profile", "*.icp"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r") as handle:
                content = handle.read()
        except OSError as exc:
            messagebox.showerror("Ingest Config Creator", f"Could not read profile:\n{exc}")
            return

        profile = {}
        for line in content.splitlines():
            if "=" not in line:
                continue
            name, _, value = line.partition("=")
            profile[name.strip()] = value.strip()

        source_type = profile.get("sourcetype", "").upper()
        if source_type in SOURCE_TYPES:
            self._set_source_type(source_type)

        for key in ICP_KEYS:
            if key in self._entries:
                self._set_entry(key, profile.get(key, ""))

        self._profile_summary.configure(text="Loaded " + os.path.basename(path))
        self._append_log(f'::Loaded profile from "{path}"')

    def _collect_params(self):
        return {key: entry.get().strip() for key, entry in self._entries.items()}

    def _validate(self, source_type, params):
        errors = []

        if not params["ddfile"]:
            errors.append("Data dictionary file is required.")
        elif not os.path.isfile(params["ddfile"]):
            errors.append(f"Data dictionary file not found:\n{params['ddfile']}")

        for key, label in (("client", "Client abbreviation"), ("database", "Database name"), ("sourcename", "Source name")):
            if not params[key]:
                errors.append(f"{label} is required.")

        if source_type == "FF":
            if not params["delimiter"]:
                errors.append("Column delimiter is required for Flat File sources.")
            if "." not in params["fileimportmatch"]:
                errors.append("File import match pattern is required and must end with a file extension.")

        if params["reporootfolder"] and not os.path.isdir(params["reporootfolder"]):
            errors.append(f"Repo root folder not found:\n{params['reporootfolder']}")

        return errors

    def _run(self):
        if self._worker and self._worker.is_alive():
            return

        source_type = self._source_type.get()
        params = self._collect_params()

        errors = self._validate(source_type, params)
        if errors:
            messagebox.showerror("Ingest Config Creator", "\n\n".join(errors))
            return

        params["sourcetype"] = source_type
        params["client"] = params["client"].upper()
        params["database"] = params["database"].upper()
        if source_type == "KIP" and params["sourcename"].upper() == "ARCHTICS":
            params["sourcename"] = "archtics-api"
        else:
            params["sourcename"] = params["sourcename"].capitalize()
        if params["reporootfolder"]:
            params["reporootfolder"] = os.path.normpath(params["reporootfolder"]) + os.sep

        self._output_folder = ""
        self._open_button.configure(state="disabled")
        self._run_button.configure(state="disabled", text="Running...")
        self._progress.start()

        self._append_log("=" * 80)
        self._append_log(f"Creating {source_type} config resources...")

        self._worker = threading.Thread(target=self._run_worker, args=(source_type, params), daemon=True)
        self._worker.start()

    def _run_worker(self, source_type, params):
        writer = _QueueWriter(self._log_queue)
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = writer

        result = None
        error = None
        try:
            if source_type == "AUD":
                result = ingestconfigcreator_aud(srcType="AUD", ui_params=params)
            else:
                result = ingestconfigcreator_prefect(srcType=source_type, ui_params=params)
        except SystemExit as exc:
            error = f"Creator exited early (code {exc.code})."
        except Exception:
            error = traceback.format_exc()
        finally:
            sys.stdout, sys.stderr = saved_stdout, saved_stderr

        self._log_queue.put(("__done__", result, error))

    def _drain_log_queue(self):
        try:
            while True:
                item = self._log_queue.get_nowait()
                if isinstance(item, tuple) and item and item[0] == "__done__":
                    self._on_run_complete(item[1], item[2])
                else:
                    self._append_log(item)
        except queue.Empty:
            pass
        self.after(100, self._drain_log_queue)

    def _on_run_complete(self, result, error):
        self._progress.stop()
        self._progress.set(0)
        self._run_button.configure(state="normal", text="Create config")

        if error:
            self._append_log(error)
            self._append_log("Run failed.")
            messagebox.showerror("Ingest Config Creator", "Run failed. See log for details.")
            return

        self._output_folder = (result or {}).get("outputfolder", "")
        if self._output_folder and os.path.isdir(self._output_folder):
            self._open_button.configure(state="normal")
            self._append_log(f"Output folder: {self._output_folder}")

        self._append_log("Done.")

    def _open_output_folder(self):
        if self._output_folder and os.path.isdir(self._output_folder):
            os.startfile(self._output_folder)

    # ------------------------------------------------------------------
    # log helpers
    # ------------------------------------------------------------------
    def _append_log(self, message):
        self._log.configure(state="normal")
        self._log.insert("end", f"{message}\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    def _on_close(self):
        if self._worker and self._worker.is_alive():
            if not messagebox.askokcancel("Ingest Config Creator", "A run is still in progress. Quit anyway?"):
                return
        self.destroy()


def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    IngestConfigCreatorUI().mainloop()


if __name__ == "__main__":
    main()
