# tools_launcher.py -- part of the public-tools collection.
# Copyright (C) 2026 Chad Aaland.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  It is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License at <https://www.gnu.org/licenses/> for details.
#
# Third-party components and their licenses: see THIRD_PARTY_NOTICES.md.
"""public-tools Launcher.

A tiny tkinter front end for the tools in this repository: one window with a
Launch button per tool, plus a one-click "set up dependencies" button. It
shells out to each tool's existing entry point, so every tool keeps its own
behavior -- the launcher just saves you from hunting for the right .bat.

Stdlib only (tkinter / subprocess / webbrowser); no third-party dependencies
of its own. Double-click Tools.bat, or run `python tools_launcher.py`.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parent

# Tool registry.  "kind" decides how the launcher invokes it:
#   filepicker -> the script opens its own file dialog (run as-is)
#   folder     -> operates on a folder; we ask which one and pass it as argv[1]
#   flask      -> a local web app; start the server and open the browser
TOOLS = [
    {"folder": "pdf-to-csv", "script": "pdf_to_csv.py", "kind": "filepicker",
     "name": "PDF to CSV",
     "desc": "Extract every table from a PDF into CSV, with a preview step."},
    {"folder": "pdf-to-markdown", "script": "pdf_to_markdown.py", "kind": "filepicker",
     "name": "PDF to Markdown",
     "desc": "Convert a PDF into clean, LLM-ready Markdown."},
    {"folder": "ocr-pdf", "script": "ocr_pdf.py", "kind": "filepicker",
     "name": "OCR PDF",
     "desc": "Make a scanned PDF (or image) searchable; also writes a .txt."},
    {"folder": "extract-convert-combine-to-pdf",
     "script": "Extract_Convert_Combine to PDF.py", "kind": "folder",
     "name": "Extract / Convert / Combine to PDF",
     "desc": "Package a folder of receipts (.msg, .heic, images, PDFs) into one PDF."},
    {"folder": "w9-catchup", "script": "app.py", "kind": "flask",
     "url": "http://127.0.0.1:5099/",
     "name": "W-9 Catch-Up",
     "desc": "Local web app: OCR and review a backlog of W-9 PDFs."},
]


def tool_script_path(tool: dict) -> Path:
    return ROOT / tool["folder"] / tool["script"]


def _python_exe(windowless: bool = False) -> str:
    """Path to the Python interpreter to launch tools with.  For GUI tools we
    prefer pythonw.exe (Windows) so no console window flashes; for console
    tools we keep python.exe so their output / errors stay visible."""
    exe = Path(sys.executable)
    if windowless and os.name == "nt":
        pyw = exe.with_name("pythonw.exe")
        if pyw.exists():
            return str(pyw)
    return str(exe)


def _launch_command(tool: dict, target: str | None = None) -> tuple[list[str], str]:
    """Pure helper (no side effects): return (args, cwd) for launching a tool.
    `target` is the chosen folder for kind == 'folder'."""
    script = tool_script_path(tool)
    kind = tool["kind"]
    if kind == "folder":
        if not target:
            raise ValueError("folder tools require a target directory")
        # The script reads its target from argv[1]; run it from that folder.
        return ([_python_exe(), str(script), target], target)
    if kind == "flask":
        # windowless: the server runs in the background and the browser opens,
        # so there's no console for a non-technical user to puzzle over.
        return ([_python_exe(windowless=True), str(script)], str(script.parent))
    # filepicker (and default): the script opens its own dialog
    return ([_python_exe(windowless=True), str(script)], str(script.parent))


def requirements_files() -> list[Path]:
    """Every tool's requirements.txt that actually exists (some tools
    auto-install their own deps and have none)."""
    out = []
    for t in TOOLS:
        req = ROOT / t["folder"] / "requirements.txt"
        if req.exists():
            out.append(req)
    return out


def launch_tool(tool: dict, status=None) -> None:
    """Launch a tool in its own process, leaving this window open."""
    script = tool_script_path(tool)
    if not script.exists():
        messagebox.showerror("Missing tool",
                             f"Could not find:\n{script}\n\n"
                             "Make sure the launcher sits in the repo root "
                             "next to the tool folders.")
        return
    target = None
    if tool["kind"] == "folder":
        target = filedialog.askdirectory(
            title=f"{tool['name']}: choose the folder to process")
        if not target:
            if status:
                status("Cancelled.")
            return
    try:
        args, cwd = _launch_command(tool, target)
        subprocess.Popen(args, cwd=cwd)
    except Exception as exc:  # pragma: no cover - defensive
        messagebox.showerror("Launch failed", f"{tool['name']}:\n{exc}")
        return
    if tool["kind"] == "flask":
        threading.Timer(2.5, lambda: webbrowser.open(tool["url"])).start()
        if status:
            status(f"Starting {tool['name']} -- opening {tool['url']}")
    elif tool["kind"] == "folder":
        if status:
            status(f"Launched {tool['name']} on {target}")
    else:
        if status:
            status(f"Launched {tool['name']}.")


def install_dependencies(status=None) -> None:
    """Run `pip install -r ...` for every tool that has a requirements file,
    in one new console window so the user can watch progress."""
    reqs = requirements_files()
    if not reqs:
        messagebox.showinfo("Dependencies",
                            "No requirements files found (the tools that have "
                            "dependencies auto-install them on first run).")
        return
    args = [_python_exe(), "-m", "pip", "install"]
    for r in reqs:
        args += ["-r", str(r)]
    flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    subprocess.Popen(args, cwd=str(ROOT), creationflags=flags)
    if status:
        status(f"Installing dependencies for {len(reqs)} tool(s) in a new window...")


# ---------------- UI ----------------

def build_ui() -> tk.Tk:
    root = tk.Tk()
    root.title("public-tools Launcher")
    root.minsize(560, 440)
    try:
        ttk.Style().theme_use("vista" if os.name == "nt" else "clam")
    except tk.TclError:
        pass

    outer = ttk.Frame(root, padding=14)
    outer.pack(fill="both", expand=True)

    ttk.Label(outer, text="public-tools", font=("Segoe UI", 16, "bold")).pack(anchor="w")
    ttk.Label(outer, text="Pick a tool to launch. Each opens in its own window.",
              foreground="#555").pack(anchor="w", pady=(0, 10))

    status_var = tk.StringVar(value="")

    def set_status(msg: str) -> None:
        status_var.set(msg)

    for t in TOOLS:
        row = ttk.Frame(outer, padding=(0, 6))
        row.pack(fill="x")
        left = ttk.Frame(row)
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text=t["name"], font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(left, text=t["desc"], foreground="#666",
                  wraplength=380, justify="left").pack(anchor="w")
        ttk.Button(row, text="Launch", width=10,
                   command=lambda t=t: launch_tool(t, set_status)).pack(side="right")
        ttk.Separator(outer, orient="horizontal").pack(fill="x")

    bottom = ttk.Frame(outer, padding=(0, 10))
    bottom.pack(fill="x", side="bottom")
    ttk.Button(bottom, text="Set up / update dependencies",
               command=lambda: install_dependencies(set_status)).pack(side="left")
    ttk.Button(bottom, text="Quit", command=root.destroy).pack(side="right")
    ttk.Label(outer, textvariable=status_var, foreground="#246",
              wraplength=520, justify="left").pack(anchor="w", side="bottom", fill="x")
    return root


def _relaunch_windowless_if_needed() -> None:
    """On Windows, being started via python.exe carries a console window that
    lingers behind the GUI and confuses non-technical users. If that's how we
    were started, relaunch under pythonw.exe (no console) and exit. No-op when
    already windowless, when pythonw can't be found, or on non-Windows."""
    if os.name != "nt":
        return
    exe = Path(sys.executable)
    if exe.name.lower() != "python.exe":
        return  # already pythonw / embedded -> no console to shed
    pyw = exe.with_name("pythonw.exe")
    if not pyw.exists():
        return  # nothing to relaunch with; run as-is
    try:
        subprocess.Popen([str(pyw), os.path.abspath(__file__), *sys.argv[1:]])
    except Exception:
        return  # fall through and run with the console rather than not at all
    sys.exit(0)


def main() -> None:
    _relaunch_windowless_if_needed()
    build_ui().mainloop()


if __name__ == "__main__":
    main()
