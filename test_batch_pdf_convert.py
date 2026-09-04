"""Unit tests for batch_pdf_convert.py.

These mock pdfminer's extract_text() so they don't depend on a real PDF
file or the vendored docling-main/ content - they only exercise this
repo's own file-handling logic (directory checks, filename generation,
extension matching, JSON output).
"""
import json

import pytest

import batch_pdf_convert as bpc


def test_get_output_filename():
    result = bpc.get_output_filename("some/dir/paper.pdf", "out")
    assert result == "out/paper.json" or result == "out\\paper.json"


def test_create_output_directory_creates_missing_dir(tmp_path):
    target = tmp_path / "nested" / "output"
    assert not target.exists()
    bpc.create_output_directory(str(target))
    assert target.is_dir()


def test_batch_convert_pdfs_raises_on_missing_input_dir(tmp_path):
    missing = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError):
        bpc.batch_convert_pdfs(str(missing), str(tmp_path / "out"))


def test_batch_convert_pdfs_matches_pdf_and_PDF_case_insensitively(tmp_path, monkeypatch):
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    (input_dir / "lowercase.pdf").write_bytes(b"%PDF-fake")
    (input_dir / "uppercase.PDF").write_bytes(b"%PDF-fake")
    output_dir = tmp_path / "out"

    monkeypatch.setattr(bpc, "extract_text", lambda path: "some extracted text")

    successful, failed = bpc.batch_convert_pdfs(str(input_dir), str(output_dir))

    assert successful == 2
    assert failed == 0
    assert (output_dir / "lowercase.json").exists()
    assert (output_dir / "uppercase.json").exists()


def test_extract_pdf_to_json_returns_false_and_skips_write_when_no_text(tmp_path, monkeypatch):
    monkeypatch.setattr(bpc, "extract_text", lambda path: "")
    output_path = tmp_path / "should_not_be_created.json"

    result = bpc.extract_pdf_to_json("irrelevant.pdf", str(output_path))

    assert result is False
    assert not output_path.exists()


def test_extract_pdf_to_json_writes_expected_structure(tmp_path, monkeypatch):
    monkeypatch.setattr(bpc, "extract_text", lambda path: "hello world")
    output_path = tmp_path / "result.json"

    result = bpc.extract_pdf_to_json("paper.pdf", str(output_path))

    assert result is True
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["content"] == "hello world"
    assert data["metadata"]["source_file"] == "paper.pdf"
    assert data["metadata"]["character_count"] == len("hello world")
