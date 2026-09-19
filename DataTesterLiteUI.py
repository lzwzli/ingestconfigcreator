"""Desktop UI (customtkinter) front-end for Data Tester Lite."""

import os
import queue
import sys
import threading
import traceback
import webbrowser

# the tester modules resolve imports relative to this folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
os.chdir(SCRIPT_DIR)

import customtkinter as ctk
from tkinter import filedialog, messagebox

from Library.Class.DataTester.RunTestsFromFile import RunTestsFromFile
from Library.Class.Logger import Logger
from Library.FunctionFiles.Functions import CreateDTP, getProfileDict, loadProfileVars, outputTestFolder, outputFolder, filewrite
from version import version, releasedate

DTP_KEYS = ["client", "database", "sf_user", "role", "testfilepath", "filter"]
HELP_URL = "https://kraftanalyticsgroup.atlassian.net/wiki/spaces/KU/pages/3938320572/The+Ingest+Config+Creator+app#Data-Testing"


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


class DataTesterLiteUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"Data Tester Lite {version}")
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

        self.after(100, self._drain_log_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # layout
    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Data Tester Lite", font=self._title_font).grid(
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
            header, text="Load profile (.dtp)", width=150, command=self._load_profile
        ).grid(row=1, column=3, padx=(0, 16), sticky="e")

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=16, pady=(12, 0), sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self._entries = {}
        row = 0

        row = self._add_row(form, row, "testfilepath", "Test definition file *", browse="file")
        row = self._add_row(form, row, "client", "Client abbreviation *")
        row = self._add_row(form, row, "database", "Database name *")
        row = self._add_row(form, row, "sf_user", "Snowflake user (email) *")
        row = self._add_row(form, row, "role", "Snowflake role *")
        row = self._add_row(form, row, "filter", "Test filter (i.e. 1-4 or search string)")

        ctk.CTkLabel(
            form,
            text='* required.  Filter is optional - leave blank to run all tests.',
            font=self._label_font,
            text_color=("gray40", "gray60"),
        ).grid(row=row, column=0, columnspan=3, padx=16, pady=(4, 16), sticky="w")

    def _add_row(self, parent, row, key, label, browse=None):
        lbl = ctk.CTkLabel(parent, text=label, font=self._label_font, anchor="w")
        lbl.grid(row=row, column=0, padx=(16, 8), pady=5, sticky="w")

        entry = ctk.CTkEntry(parent, placeholder_text=label)
        span = 1 if browse else 2
        entry.grid(row=row, column=1, columnspan=span, padx=8, pady=5, sticky="ew")
        self._entries[key] = entry

        if browse:
            cmd = self._browse_file if browse == "file" else self._browse_folder
            btn = ctk.CTkButton(parent, text="Browse", width=90, command=lambda k=key: cmd(k))
            btn.grid(row=row, column=2, padx=(8, 16), pady=5, sticky="e")

        return row + 1

    def _build_actions(self):
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, padx=16, pady=(12, 0), sticky="ew")
        actions.grid_columnconfigure(3, weight=1)

        self._run_button = ctk.CTkButton(actions, text="Run tests", width=160, command=self._run)
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
    def _browse_file(self, key):
        path = filedialog.askopenfilename(
            title="Select SQL test definition file", filetypes=[("SQL", "*.sql"), ("All files", "*.*")]
        )
        if path:
            self._set_entry(key, os.path.normpath(path))

    def _browse_folder(self, key):
        path = filedialog.askdirectory(title="Select folder")
        if path:
            self._set_entry(key, os.path.normpath(path) + os.sep)

    def _set_entry(self, key, value):
        entry = self._entries[key]
        entry.delete(0, "end")
        entry.insert(0, value or "")

    def _load_profile(self):
        path = filedialog.askopenfilename(
            title="Select data tester run profile", filetypes=[("Data Tester Profile", "*.dtp"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r") as handle:
                content = handle.read()
        except OSError as exc:
            messagebox.showerror("Data Tester Lite", f"Could not read profile:\n{exc}")
            return

        profileDict = getProfileDict(profilelist=content.split("\n"))

        for key in DTP_KEYS:
            if key in self._entries:
                self._set_entry(key, loadProfileVars(profileDict, varname=key))

        self._profile_summary.configure(text="Loaded " + os.path.basename(path))
        self._append_log(f'::Loaded profile from "{path}"')

    def _collect_params(self):
        return {key: entry.get().strip() for key, entry in self._entries.items()}

    def _validate(self, params):
        errors = []

        if not params["testfilepath"]:
            errors.append("Test definition file is required.")
        elif not os.path.isfile(params["testfilepath"]):
            errors.append(f"Test definition file not found:\n{params['testfilepath']}")

        for key, label in (
            ("client", "Client abbreviation"),
            ("database", "Database name"),
            ("sf_user", "Snowflake user"),
            ("role", "Snowflake role"),
        ):
            if not params[key]:
                errors.append(f"{label} is required.")

        if params["client"] and params["database"] and params["client"].lower() not in params["database"].lower():
            errors.append(f'Database "{params["database"]}" is incorrect for Client "{params["client"]}".')

        return errors

    def _run(self):
        if self._worker and self._worker.is_alive():
            return

        params = self._collect_params()

        errors = self._validate(params)
        if errors:
            messagebox.showerror("Data Tester Lite", "\n\n".join(errors))
            return

        params["client"] = params["client"].upper()
        params["database"] = params["database"].upper()
        if not params["filter"]:
            params["filter"] = "0"

        self._output_folder = ""
        self._open_button.configure(state="disabled")
        self._run_button.configure(state="disabled", text="Running...")
        self._progress.start()

        self._append_log("=" * 80)
        self._append_log("Running tests...")

        self._worker = threading.Thread(target=self._run_worker, args=(params,), daemon=True)
        self._worker.start()

    def _run_worker(self, params):
        writer = _QueueWriter(self._log_queue)
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = writer

        runlog = Logger()
        result = None
        error = None
        try:
            testfilepath = params["testfilepath"]
            outputfolder = outputTestFolder(testfilepath)

            runlog.log(f"::Test Definition File = {testfilepath}")
            runlog.log(f"::Filter = {params['filter']}")
            runlog.log(f"::Client = {params['client']}")
            runlog.log(f"::Database = {params['database']}")
            runlog.log(f"::User = {params['sf_user']}")
            runlog.log(f"::Role = {params['role']}")
            runlog.log("")

            profilename = f"DataTesterProfile_{params['client']}_{params['database']}_RunTests.dtp"
            dtplogmsg = CreateDTP(
                profilename=profilename,
                client=params["client"],
                database=params["database"],
                role=params["role"],
                testfilepath=testfilepath,
                outputfolder=outputfolder,
                sf_user=params["sf_user"],
                testfilter=params["filter"],
            )
            runlog.log(dtplogmsg)

            runTest = RunTestsFromFile(runlog)
            runTest.setTestsInfo(
                client=params["client"],
                database=params["database"],
                sf_user=params["sf_user"],
                role=params["role"],
                test_file_path=testfilepath,
                filter=params["filter"],
            )

            filename = ""
            resultsJSONfilename = ""
            try:
                outputfolder, filename, resultsJSONfilename = runTest.execTests()
            except SystemExit:
                outputfolder = outputFolder(testfilepath)

            runlog_filename = f"{filename} Run Log.txt"
            runlog.log("")
            runlogmsg = runlog.out()

            filewrite(folder=outputfolder, filename=runlog_filename, content=runlogmsg)

            result = {"outputfolder": outputfolder, "filename": filename, "resultsJSONfilename": resultsJSONfilename}
        except SystemExit as exc:
            error = f"Run exited early (code {exc.code})."
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
        self._run_button.configure(state="normal", text="Run tests")

        if error:
            self._append_log(error)
            self._append_log("Run failed.")
            messagebox.showerror("Data Tester Lite", "Run failed. See log for details.")
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
            if not messagebox.askokcancel("Data Tester Lite", "A run is still in progress. Quit anyway?"):
                return
        self.destroy()


def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    DataTesterLiteUI().mainloop()


if __name__ == "__main__":
    main()
