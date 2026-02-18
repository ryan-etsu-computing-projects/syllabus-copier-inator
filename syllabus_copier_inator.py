"""
Syllabus Copier-inator 1000
A Tkinter GUI for copying syllabi to per-section filenames.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import platform
import subprocess
import shutil
from pathlib import Path


# ── helpers ──────────────────────────────────────────────────────────────────

def list_pdfs(folder: str) -> list[str]:
    p = Path(folder)
    return [f.name for f in sorted(p.glob("*.pdf"))]


def build_filename(subject, course, section, crn, last_name) -> str:
    return f"{subject}_{course}_{section}_CRN_{crn}_{last_name}.pdf"


def increment_section(section: str) -> str:
    try:
        return str(int(section) + 1).zfill(3)
    except ValueError:
        return section


# ── row widget ────────────────────────────────────────────────────────────────

class SyllabusRow:
    """One data row in the table."""

    def __init__(self, master_frame, pdf_options: list[str],
                 on_remove, on_copy_down, row_index: int):
        self.master_frame = master_frame
        self.on_remove = on_remove
        self.on_copy_down = on_copy_down

        self.frame = tk.Frame(master_frame, bd=1, relief=tk.RIDGE, bg="#f9f9f9")
        self.frame.pack(fill=tk.X, padx=4, pady=2)

        # ── Syllabus dropdown ──
        self.syllabus_var = tk.StringVar()
        self.syllabus_combo = ttk.Combobox(self.frame, textvariable=self.syllabus_var,
                                           values=pdf_options, width=34, state="readonly")
        if pdf_options:
            self.syllabus_combo.current(0)
        self.syllabus_combo.grid(row=0, column=0, padx=(6, 2), pady=4)

        # ── Subject Code (4 chars) ──
        self.subject_var = tk.StringVar(value="CSCI")
        vcmd_subj = master_frame.register(lambda v: len(v) <= 4)
        self.subject_entry = tk.Entry(self.frame, textvariable=self.subject_var,
                                      width=6, validate="key",
                                      validatecommand=(vcmd_subj, "%P"))
        self.subject_entry.grid(row=0, column=1, padx=2, pady=4)

        # ── Course Code (4 digits) ──
        self.course_var = tk.StringVar(value="1100")
        vcmd_course = master_frame.register(lambda v: v.isdigit() and len(v) <= 4 or v == "")
        self.course_entry = tk.Entry(self.frame, textvariable=self.course_var,
                                     width=6, validate="key",
                                     validatecommand=(vcmd_course, "%P"))
        self.course_entry.grid(row=0, column=2, padx=2, pady=4)

        # ── Section (3 digits) ──
        self.section_var = tk.StringVar(value="001")
        vcmd_sec = master_frame.register(lambda v: v.isdigit() and len(v) <= 3 or v == "")
        self.section_entry = tk.Entry(self.frame, textvariable=self.section_var,
                                      width=5, validate="key",
                                      validatecommand=(vcmd_sec, "%P"))
        self.section_entry.grid(row=0, column=3, padx=2, pady=4)

        # ── Last Name ──
        self.last_var = tk.StringVar(value="")
        self.last_entry = tk.Entry(self.frame, textvariable=self.last_var, width=12)
        self.last_entry.grid(row=0, column=4, padx=2, pady=4)
        self.last_var.trace_add("write", self._capitalize_last)
        self._capitalizing = False

        # ── CRN (5 digits) ──
        self.crn_var = tk.StringVar(value="00000")
        vcmd_crn = master_frame.register(lambda v: v.isdigit() and len(v) <= 5 or v == "")
        self.crn_entry = tk.Entry(self.frame, textvariable=self.crn_var,
                                  width=7, validate="key",
                                  validatecommand=(vcmd_crn, "%P"))
        self.crn_entry.grid(row=0, column=5, padx=2, pady=4)

        # ── Copy Down button ──
        self.copy_btn = tk.Button(self.frame, text="⬇ Copy Down", bg="#d0e8ff",
                                  command=lambda: on_copy_down(self), relief=tk.FLAT,
                                  cursor="hand2", padx=4)
        self.copy_btn.grid(row=0, column=6, padx=2, pady=4)

        # ── Remove button ──
        self.remove_btn = tk.Button(self.frame, text="✕ Remove", bg="#ffcccc",
                                    command=lambda: on_remove(self), relief=tk.FLAT,
                                    cursor="hand2", padx=4)
        self.remove_btn.grid(row=0, column=7, padx=(2, 6), pady=4)

    def _capitalize_last(self, *_):
        if self._capitalizing:
            return
        self._capitalizing = True
        val = self.last_var.get()
        if val:
            self.last_var.set(val[0].upper() + val[1:])
        self._capitalizing = False

    def get_data(self) -> dict:
        return {
            "syllabus": self.syllabus_var.get(),
            "subject":  self.subject_var.get().strip().upper(),
            "course":   self.course_var.get().strip(),
            "section":  self.section_var.get().strip().zfill(3),
            "last":     self.last_var.get().strip(),
            "crn":      self.crn_var.get().strip(),
        }

    def update_pdf_options(self, pdf_options: list[str]):
        self.syllabus_combo["values"] = pdf_options
        if pdf_options and self.syllabus_var.get() not in pdf_options:
            self.syllabus_combo.current(0)

    def destroy(self):
        self.frame.destroy()


# ── main app ──────────────────────────────────────────────────────────────────

class SyllabusCopierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Syllabus Copier-inator 1000")
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")

        self.syllabus_folder = tk.StringVar(value="")
        self.pdf_options: list[str] = []
        self.rows: list[SyllabusRow] = []

        self._build_ui()
        self.minsize(820, 300)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Title bar ──
        title_lbl = tk.Label(self, text="Syllabus Copier-inator 1000",
                             font=("Helvetica", 14, "bold"), bg="#3a3a3a", fg="white",
                             pady=6)
        title_lbl.pack(fill=tk.X)

        # ── Folder selection row ──
        folder_frame = tk.Frame(self, bg="#e8e8e8", bd=1, relief=tk.SUNKEN)
        folder_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(folder_frame, text="Syllabus Folder:", bg="#e8e8e8",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(8, 4), pady=6)

        self.folder_lbl = tk.Label(folder_frame, textvariable=self.syllabus_folder,
                                   bg="white", relief=tk.SUNKEN, anchor="w",
                                   width=48, padx=4)
        self.folder_lbl.pack(side=tk.LEFT, pady=6)

        tk.Button(folder_frame, text="📂 Browse…", command=self._browse_folder,
                  bg="#a4d1fc", fg="black", relief=tk.FLAT, cursor="hand2",
                  padx=8).pack(side=tk.LEFT, padx=8, pady=6)

        tk.Button(folder_frame, text="↺ Refresh PDFs", command=self._refresh_pdfs,
                  bg="#b6e894", fg="black", relief=tk.FLAT, cursor="hand2",
                  padx=8).pack(side=tk.LEFT, padx=0, pady=6)

        # ── Column headers ──
        hdr = tk.Frame(self, bg="#dce6f1")
        hdr.pack(fill=tk.X, padx=4, pady=(4, 0))
        headers = [
            ("Syllabus (PDF)", 34),
            ("Subj", 4),
            ("Course", 6),
            ("Sec", 5),
            ("Last Name", 10),
            ("CRN", 3),
            ("", 10),
            ("", 8),
        ]
        for text, w in headers:
            tk.Label(hdr, text=text, bg="#dce6f1", font=("Helvetica", 9, "bold"),
                     width=w, anchor="w").pack(side=tk.LEFT, padx=2, pady=2)

        tk.Button(hdr, text="+ Add Row", bg="#c6efce", font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, cursor="hand2", command=self._add_row,
                  padx=6).pack(side=tk.RIGHT, padx=8)

        # ── Scrollable rows area ──
        container = tk.Frame(self, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        self.canvas = tk.Canvas(container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg="#f0f0f0")

        self.rows_frame.bind("<Configure>",
                             lambda e: self.canvas.configure(
                                 scrollregion=self.canvas.bbox("all")))

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(
                             self.canvas_window, width=e.width))

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # mouse-wheel scrolling
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(
                                 int(-1 * (e.delta / 120)), "units"))

        # ── Status bar ──
        self.status_var = tk.StringVar(value="Ready. Select a syllabus folder to begin.")
        status_bar = tk.Label(self, textvariable=self.status_var,
                              bg="#e0e0e0", anchor="w", padx=8,
                              font=("Helvetica", 9, "italic"))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # ── Progress bar ──
        prog_frame = tk.Frame(self, bg="#f0f0f0")
        prog_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=2)

        self.progress = ttk.Progressbar(prog_frame, orient="horizontal",
                                        mode="determinate", length=400)
        self.progress.pack(side=tk.LEFT, padx=(0, 8))

        # ── Bottom buttons ──
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=6)

        tk.Button(btn_frame, text="🗂  Copy 'Em!", command=self._copy_files,
                  bg="#ffe699", font=("Helvetica", 11, "bold"),
                  relief=tk.RAISED, cursor="hand2", padx=16, pady=6).pack(side=tk.LEFT)

        tk.Button(btn_frame, text="Clear All Rows", command=self._clear_rows,
                  bg="#f4b942", relief=tk.FLAT, cursor="hand2",
                  padx=10, pady=6).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_frame, text="Exit", command=self.destroy,
                  bg="#fc8a8a", fg="black", font=("Helvetica", 10),
                  relief=tk.FLAT, cursor="hand2",
                  padx=12, pady=6).pack(side=tk.RIGHT)

    # ── actions ───────────────────────────────────────────────────────────────

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Syllabus Folder")
        if folder:
            self.syllabus_folder.set(folder)
            self._refresh_pdfs()

    def _refresh_pdfs(self):
        folder = self.syllabus_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder first.")
            return
        self.pdf_options = list_pdfs(folder)
        for row in self.rows:
            row.update_pdf_options(self.pdf_options)
        n = len(self.pdf_options)
        self.status_var.set(f"Found {n} PDF{'s' if n != 1 else ''} in folder.")

    def _add_row(self, syllabus=None, subject="CSCI", course="1100",
                 section="001", last="", crn="00000"):
        if not self.pdf_options and self.syllabus_folder.get():
            self._refresh_pdfs()

        row = SyllabusRow(self.rows_frame, self.pdf_options,
                          on_remove=self._remove_row,
                          on_copy_down=self._copy_down_row,
                          row_index=len(self.rows))
        # pre-fill
        if syllabus and syllabus in self.pdf_options:
            row.syllabus_var.set(syllabus)
        row.subject_var.set(subject)
        row.course_var.set(course)
        row.section_var.set(section)
        row.last_var.set(last)
        row.crn_var.set(crn)

        self.rows.append(row)
        self._scroll_bottom()

    def _remove_row(self, row: SyllabusRow):
        self.rows.remove(row)
        row.destroy()

    def _copy_down_row(self, row: SyllabusRow):
        d = row.get_data()
        new_section = increment_section(d["section"])
        idx = self.rows.index(row)
        # insert after this row by temporarily holding subsequent rows
        # Simplest: just append (ordering matches visual since we always append)
        self._add_row(
            syllabus=d["syllabus"],
            subject=d["subject"],
            course=d["course"],
            section=new_section,
            last=d["last"],
            crn="00000",
        )
        # Move the new row's frame right after the current one visually
        # by re-packing. We do this by re-ordering pack order.
        new_row = self.rows[-1]
        # Remove from pack and re-insert after the source row's frame
        new_row.frame.pack_forget()
        new_row.frame.pack(fill=tk.X, padx=4, pady=2,
                           after=row.frame)
        # Update rows list order to match visual
        self.rows.remove(new_row)
        self.rows.insert(idx + 1, new_row)

    def _clear_rows(self):
        if messagebox.askyesno("Clear All", "Remove all rows?"):
            for row in self.rows[:]:
                row.destroy()
            self.rows.clear()

    def _scroll_bottom(self):
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ── validation before copy ────────────────────────────────────────────────

    def _validate_rows(self) -> list[str]:
        errors = []
        crns_seen = {}
        for i, row in enumerate(self.rows, 1):
            d = row.get_data()
            if not d["syllabus"]:
                errors.append(f"Row {i}: No syllabus selected.")
            if len(d["subject"]) == 0:
                errors.append(f"Row {i}: Subject code is empty.")
            if not d["course"].isdigit() or len(d["course"]) != 4:
                errors.append(f"Row {i}: Course code must be exactly 4 digits.")
            if not d["section"].isdigit() or len(d["section"]) != 3:
                errors.append(f"Row {i}: Section must be exactly 3 digits.")
            if not d["last"]:
                errors.append(f"Row {i}: Last name is empty.")
            if not d["crn"].isdigit() or len(d["crn"]) != 5:
                errors.append(f"Row {i}: CRN must be exactly 5 digits.")
            if d["crn"] != "00000":
                if d["crn"] in crns_seen:
                    errors.append(
                        f"Row {i}: CRN {d['crn']} duplicates row {crns_seen[d['crn']]}.")
                else:
                    crns_seen[d["crn"]] = i
        return errors
    
    ######## Open folder (after copy)
    def open_folder_cross_platform(self, folder_path='.'):
        """Opens the specified folder in the system's default file manager."""
        
        # Ensure the path is an absolute path
        abs_path = os.path.abspath(folder_path)

        if platform.system() == "Windows":
            # Use os.startfile on Windows
            os.startfile(abs_path)
        elif platform.system() == "Darwin":
            # Use 'open' command on macOS
            subprocess.Popen(["open", abs_path])
        else:
            # Use 'xdg-open' command on Linux/Unix variants
            subprocess.Popen(["xdg-open", abs_path])

    # ── copy operation ────────────────────────────────────────────────────────

    def _copy_files(self):
        folder = self.syllabus_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid syllabus folder first.")
            return
        if not self.rows:
            messagebox.showwarning("Nothing to do", "Add at least one row first.")
            return

        errors = self._validate_rows()
        if errors:
            messagebox.showerror("Validation Errors",
                                 "\n".join(errors[:10]) +
                                 (f"\n…and {len(errors)-10} more." if len(errors) > 10 else ""))
            return

        copies_root = Path(folder) / "copies"
        copies_root.mkdir(exist_ok=True)

        total = len(self.rows)
        self.progress["maximum"] = total
        self.progress["value"] = 0

        results = []
        for i, row in enumerate(self.rows):
            d = row.get_data()
            src = Path(folder) / d["syllabus"]
            if not src.exists():
                results.append(f"⚠ Skipped: source not found → {src.name}")
                continue

            stem = src.stem
            dest_dir = copies_root / f"{stem}_copies"
            dest_dir.mkdir(parents=True, exist_ok=True)

            dest_name = build_filename(d["subject"], d["course"],
                                       d["section"], d["crn"], d["last"])
            dest = dest_dir / dest_name

            try:
                shutil.copy2(src, dest)
                results.append(f"✓ {dest_name}")
            except Exception as e:
                results.append(f"✗ ERROR copying row {i+1}: {e}")

            self.progress["value"] = i + 1
            self.status_var.set(f"Copying… {i+1}/{total}")
            self.update_idletasks()

        self.status_var.set(f"Done! {total} file(s) processed. Output → {copies_root}")

        # summary popup
        summary = "\n".join(results)
        msg_title = "Copy Complete"
        if any(r.startswith("✗") for r in results):
            msg_title = "Copy Finished (with errors)"
        messagebox.showinfo(msg_title,
                            f"Output folder:\n{copies_root}\n\n{summary}")
        self.open_folder_cross_platform(copies_root)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = SyllabusCopierApp()
    app.geometry("900x500")
    app.mainloop()
