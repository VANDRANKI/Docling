# Docling

Personal PDF-to-JSON extraction workspace built on top of [Docling](https://github.com/DS4SD/docling)
(vendored in `docling-main/`) and `pdfminer.six`.

The upstream Docling project's own README used to be copy-pasted here verbatim, which
described the `docling` pip package instead of what actually lives in this repo. This
README describes the two scripts at the repo root, which are what this repo is for.

## What's here

| Path | Purpose |
|---|---|
| `pdf_extract.py` | Extracts text from a single hardcoded PDF and writes `extracted_content.json`. Meant for quick one-off checks; edit the `pdf_path` at the bottom of the file to point at a different PDF. |
| `batch_pdf_convert.py` | Converts every `*.pdf`/`*.PDF` file in an input directory to a matching JSON file in an output directory, with progress and error logging to `pdf_conversion.log`. |
| `docling-main/` | A vendored copy of the upstream [DS4SD/docling](https://github.com/DS4SD/docling) library, kept for reference and as the source of `Research_Papers_PDF_Files/` / `Research_Papers_JSON_Files/`, a curated set of research papers converted to JSON. |

## Usage

```bash
pip install pdfminer.six

# Single file (edit pdf_path in pdf_extract.py first)
python pdf_extract.py

# Batch convert a directory
python -c "from batch_pdf_convert import batch_convert_pdfs; batch_convert_pdfs('path/to/pdfs', 'path/to/output')"
```

Both scripts extract plain text only (via `pdfminer.six`), not layout, tables, or
reading order. For that, use the actual `docling` package vendored in `docling-main/`
or installed via `pip install docling` per the
[upstream project](https://github.com/DS4SD/docling).

## Output format

```json
{
  "metadata": {
    "source_file": "example.pdf",
    "extraction_date": "2026-08-31T12:00:00",
    "character_count": 12345
  },
  "content": "extracted text..."
}
```

`extracted_content.json` and `pdf_conversion.log` are run artifacts (gitignored), not
source; regenerate them by running the scripts.
