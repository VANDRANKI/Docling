"""Unit tests for pdf_extract.py.

pdfminer's extract_text() is mocked, so no real PDF is needed. The script
writes extracted_content.json into the current directory, so each test runs
inside tmp_path.
"""
import json

import pytest

import pdf_extract


@pytest.fixture(autouse=True)
def _run_in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_writes_metadata_and_content(monkeypatch, tmp_path):
    monkeypatch.setattr(pdf_extract, "extract_text", lambda path: "Hello °C world")
    pdf_extract.extract_pdf_to_json("some/dir/paper.pdf")

    raw = (tmp_path / "extracted_content.json").read_text(encoding="utf-8")
    doc = json.loads(raw)
    assert doc["content"] == "Hello °C world"
    assert doc["metadata"]["source_file"] == "paper.pdf"
    assert doc["metadata"]["character_count"] == len("Hello °C world")
    assert doc["metadata"]["extraction_date"]
    # non-ASCII is kept as characters, not \u escapes
    assert "°C" in raw


def test_empty_text_writes_no_file(monkeypatch, tmp_path):
    monkeypatch.setattr(pdf_extract, "extract_text", lambda path: "")
    pdf_extract.extract_pdf_to_json("scanned.pdf")
    assert not (tmp_path / "extracted_content.json").exists()


def test_extraction_errors_are_re_raised(monkeypatch):
    def boom(path):
        raise ValueError("not a PDF")

    monkeypatch.setattr(pdf_extract, "extract_text", boom)
    with pytest.raises(ValueError, match="not a PDF"):
        pdf_extract.extract_pdf_to_json("broken.pdf")
