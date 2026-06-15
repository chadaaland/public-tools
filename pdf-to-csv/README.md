# PDF to CSV

A double-click desktop utility that extracts every table from a PDF and
saves it as a CSV file, with a visual preview step so you can confirm
each detected table before writing.

## What it does

1. **Open a PDF** via a file-picker dialog (or pass the path on the command line)
2. **Detect tables** on each page:
   - Primary: `pymupdf`'s vector-aware table finder (accurate for ruled
     and financial tables with explicit grid lines)
   - Fallback: `pdfplumber`'s text-clustering detector (handles unruled
     tables where rows/cols are inferred from text positioning)
   - Scanned / image-only PDFs (no text layer) are **OCR'd automatically**
     with Tesseract, then the grid is rebuilt from word positions (requires
     the Tesseract engine installed; `pytesseract`/`Pillow` are auto-installed
     on first use)
3. **Stitch continuations:** consecutive pages whose header rows match are
   merged into a single CSV. The match is **fuzzy** — a repeated header that
   the detector chops at different positions page to page (so the cell splits,
   and even the column count, drift) still stitches, with rows padded to a
   common width. This is what keeps a long paginated report from fragmenting
   into one CSV per page.
4. **Show a preview dialog** with every detected table — scroll through,
   confirm the detection looks right, then save
5. **Save** as one CSV per detected table (or a single CSV if only one was
   detected) in the same folder as the source PDF

## Best for

- Financial statements, bank statements, brokerage reports
- Anything with explicit ruled grid lines (where pymupdf's vector detector excels)
- Multi-page tables with repeating headers (now tolerant of header chopping)
- Quick one-off conversions when you'd otherwise be copy/pasting cells

## Not great for

- Complex nested or merged-cell layouts
- **Form-style layouts that aren't true grids** — label/value forms or
  multi-column "vendor card" reports where each record spans several lines.
  These aren't tables, so the column detector will split text at odd
  positions (e.g. a name as `Western Wholesa` | `le Sup` | `ply, In` | `c`)
  no matter how stitching is tuned. For data like that, a purpose-built
  extractor that knows the layout is the right tool, not a generic converter.
- Tables with no grid lines AND no consistent text alignment

## Prerequisites

- **Python 3.8+**
- The dependencies in `requirements.txt`
- Optional: the [Tesseract engine](https://github.com/UB-Mannheim/tesseract/wiki)
  for OCR of scanned PDFs

## Setup

```powershell
cd pdf-to-csv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

### Double-click (Windows)

The included `PDF to CSV.bat` launcher just runs the script from its own
folder. Double-click the .bat (or, if your `.py` extension is associated
with `python.exe`, the script itself). A file-picker opens, you pick a
PDF, you get the preview dialog, click Save.

### Command line

```powershell
python pdf_to_csv.py path\to\file.pdf
```

The preview dialog still appears. Cancel out of it to abort without writing.

### Drag and drop (Windows)

If you drag a PDF onto the script or the .bat file in Explorer, Windows
passes the PDF path as `sys.argv[1]` — same as the command-line form.

## External connections

**None.** Fully local. No network calls, no cloud services. (OCR, when used,
runs against your locally installed Tesseract engine.)

## Output

For a PDF named `report.pdf`:

- If a single table is detected (the usual case for a paginated report that
  stitches cleanly), you get `report.csv`.
- If multiple distinct tables are detected, you get one file each:
  `report_table01.csv`, `report_table02.csv`, `report_table03.csv`, …

Files are written to the same folder as the source PDF.

## Tests

```powershell
cd pdf-to-csv
python -m pytest -q
```

`test_pdf_to_csv.py` covers the continuation-stitching logic, including the
fuzzy header match that prevents a paginated report from fragmenting.

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| "No tables detected" on a scanned PDF | Scanned PDFs are OCR'd automatically, but that needs the Tesseract engine installed (see link under Prerequisites). Without it, a scan yields no tables. |
| Detected table is split awkwardly across columns | The text-clustering detector misread cell boundaries. This is expected for form-style layouts that aren't true grids (see "Not great for"). Edit the CSV, or use a layout-aware extractor. |
| A paginated report came out as many CSVs | Fixed: continuation pages now stitch via fuzzy header matching. If it still splits, the pages' headers differ by more than the similarity threshold — they may genuinely be different tables. |
| Preview dialog cut off / unreadable | Resize the window. The dialog uses tkinter's default sizing which can be cramped on small displays. |
| Crash with `ModuleNotFoundError` | `pip install -r requirements.txt` wasn't run, or you're in the wrong virtualenv. |

## License

This tool is licensed under [AGPL-3.0](../LICENSE).

It depends on `pymupdf` (dual-licensed AGPL-3.0 OR Artifex commercial) and
`pdfplumber` (MIT). See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)
at the repository root for the full dependency license list.
