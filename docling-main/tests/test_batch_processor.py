"""
Tests for the batch processor module.
"""
import json
import os
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, call

from docling.utils.batch_processor import BatchProcessor, VALID_FORMATS
from docling.document_converter import DocumentConverter
from docling.datamodel.document import DoclingDocument

@pytest.fixture
def mock_converter():
    converter = Mock(spec=DocumentConverter)
    mock_doc = Mock(spec=DoclingDocument)
    mock_doc.dict.return_value = {"content": "test content"}
    mock_doc.export_to_markdown.return_value = "# Test Content"
    
    mock_result = Mock()
    mock_result.document = mock_doc
    converter.convert.return_value = mock_result
    
    return converter

@pytest.fixture
def mock_progress_callback():
    return Mock()

@pytest.fixture
def temp_dirs(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    return input_dir, output_dir

def test_init_with_custom_params(mock_converter, mock_progress_callback):
    processor = BatchProcessor(
        converter=mock_converter,
        batch_size=5,
        max_workers=3,
        progress_callback=mock_progress_callback
    )
    
    assert processor.converter == mock_converter
    assert processor.batch_size == 5
    assert processor.max_workers == 3
    assert processor.progress_callback == mock_progress_callback

def test_init_with_invalid_batch_size(mock_converter):
    processor = BatchProcessor(converter=mock_converter, batch_size=0)
    assert processor.batch_size == 1

def test_process_directory_json(mock_converter, temp_dirs, mock_progress_callback):
    input_dir, output_dir = temp_dirs
    
    # Create test files
    test_files = ["test1.pdf", "test2.pdf"]
    for file in test_files:
        (input_dir / file).touch()
    
    processor = BatchProcessor(mock_converter)
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        metadata={"test": True}
    )
    
    assert successful == 2
    assert failed == 0
    
    # Check output files
    for file in test_files:
        output_file = output_dir / f"{Path(file).stem}.json"
        assert output_file.exists()
        
        # Verify content
        content = json.loads(output_file.read_text())
        assert "metadata" in content
        assert content["metadata"]["test"] is True
        assert "content" in content
        assert content["content"]["content"] == "test content"

def test_process_directory_markdown(mock_converter, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    # Create test file
    test_file = input_dir / "test.pdf"
    test_file.touch()
    
    processor = BatchProcessor(mock_converter)
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        export_format="markdown"
    )
    
    assert successful == 1
    assert failed == 0
    
    # Check output file
    output_file = output_dir / "test.markdown"
    assert output_file.exists()
    assert output_file.read_text() == "# Test Content"

def test_process_directory_invalid_format(mock_converter, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    processor = BatchProcessor(mock_converter)
    with pytest.raises(ValueError) as exc_info:
        processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            export_format="invalid"
        )
    assert f"Valid formats: {', '.join(VALID_FORMATS)}" in str(exc_info.value)

def test_process_directory_nonexistent_input(mock_converter):
    processor = BatchProcessor(mock_converter)
    with pytest.raises(FileNotFoundError) as exc_info:
        processor.process_directory(
            input_dir="/nonexistent/dir",
            output_dir="output"
        )
    assert "Input directory not found" in str(exc_info.value)

def test_process_directory_permission_error(mock_converter, temp_dirs, monkeypatch):
    input_dir, output_dir = temp_dirs
    
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")
    
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    
    processor = BatchProcessor(mock_converter)
    with pytest.raises(PermissionError) as exc_info:
        processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir
        )
    assert "Cannot create output directory" in str(exc_info.value)

def test_process_directory_parallel(mock_converter, temp_dirs, mock_progress_callback):
    input_dir, output_dir = temp_dirs
    
    # Create test files
    test_files = [f"test{i}.pdf" for i in range(5)]
    for file in test_files:
        (input_dir / file).touch()
    
    processor = BatchProcessor(
        converter=mock_converter,
        max_workers=2,
        progress_callback=mock_progress_callback
    )
    
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        parallel=True
    )
    
    assert successful == 5
    assert failed == 0
    assert mock_progress_callback.call_count == 5

def test_process_directory_large_files(mock_converter, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    # Create many test files
    test_files = [f"test{i}.pdf" for i in range(100)]
    for file in test_files:
        (input_dir / file).touch()
    
    processor = BatchProcessor(
        converter=mock_converter,
        batch_size=10
    )
    
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir
    )
    
    assert successful == 100
    assert failed == 0

def test_process_directory_custom_extensions(mock_converter, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    # Create files with different extensions
    extensions = ["pdf", "docx", "txt"]
    for ext in extensions:
        (input_dir / f"test.{ext}").touch()
    
    processor = BatchProcessor(mock_converter)
    
    # Test each extension
    for ext in extensions:
        successful, failed = processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            file_pattern=f"*.{ext}"
        )
        assert successful == 1
        assert failed == 0

def test_process_directory_specific_errors(mock_converter, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    # Create test file
    test_file = input_dir / "test.pdf"
    test_file.touch()
    
    # Make converter raise an exception
    mock_converter.convert.side_effect = Exception("Test error")
    
    processor = BatchProcessor(mock_converter)
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir
    )
    
    assert successful == 0
    assert failed == 1

def test_process_directory_empty(mock_converter, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    processor = BatchProcessor(mock_converter)
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir
    )
    
    assert successful == 0
    assert failed == 0
