# How To Use These Tools

A small set of desktop utilities for working with PDFs and receipt files. They run on
this PC and only read or convert files you point them at. nothing here connects to
Spectrum or changes any accounting records.

---

## Before you start: Python must be installed

These tools run on Python, which is **not** bundled with them. If Python isn't already
installed on this computer, it's a one-time setup:

1. Go to https://www.python.org/downloads/ and download the latest **Windows installer (64-bit)**.
2. Run it. On the first screen, **check "Add python.exe to PATH"**, then click **Install Now**.
   (Leave the "tcl/tk and IDLE" option checked. the tools need it for their windows.)
3. That's it, one time. After that the tools just work.

Not sure if Python is already installed? Just try launching a tool (below). If a window
opens, you're set. If nothing happens or you see "python is not recognized," it isn't
installed yet.

---

## How to open the tools

Double-click **`Tools.bat`** in this folder
(`F:\Accounting Misc\Software\Tools`). A small window opens with a **Launch** button for
each tool.

The **first** time you use a given tool it may take a minute to install what it needs
(a black window shows progress). That's normal and only happens once. If you'd rather do
it all up front, click the **"Set up dependencies"** button in the launcher.

---

## The tools

### PDF to CSV
Pulls tables out of a PDF into a **CSV** (spreadsheet) file. Click Launch, pick a PDF,
review the tables it found in a preview, and save. Good for turning a report PDF into
something you can open in Excel.

### PDF to Markdown
Converts a PDF into clean plain text (**Markdown**). handy for feeding a document into an
AI tool, or for a lightweight text copy. Click Launch, pick a PDF, choose where to save.

### OCR PDF
Makes a **scanned** PDF (or an image) searchable, so you can select and copy its text. and
so the two tools above can read it. Click Launch, pick the scanned PDF or image; it writes
a searchable `<name>_ocr.pdf` and a `<name>_ocr.txt` next to the original.

### Extract / Convert / Combine to PDF
Point it at a **folder** and it does three things: pulls the real attachments out of any
`.msg` email files (skipping signature logos), converts iPhone `.heic` photos to `.jpg`,
and combines every image and PDF in the folder into **one single PDF**. Built for
packaging a folder of receipts into one file. Click Launch, then choose the folder.

---

## For scanned documents: install Tesseract (one time)

The OCR features. **OCR PDF**, plus the scan-reading fallback in **PDF to CSV** and
**PDF to Markdown**. need a free program called **Tesseract**. Without it, those tools
still work on normal (text) PDFs but will tell you Tesseract is missing when they hit a scan.

To install it once: download the Windows installer from
https://github.com/UB-Mannheim/tesseract/wiki, run it, and accept the default install
location. The tools find it automatically after that.

---

## Notes

- The launcher may also list a **W-9 Catch-Up** tool. that's a separate utility that
  connects to Spectrum for reviewing a W-9 backlog, not one of the file tools above, and
  it's outside the scope of this guide.
- These are open-source utilities (AGPL-3.0). see `LICENSE` and `THIRD_PARTY_NOTICES.md`
  in this folder.
- These tools were written by Chad Aaland; the source also lives in the `E:\Tools`
  repository.
