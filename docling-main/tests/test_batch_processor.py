"""
Tests for the batch processor module.
"""
import json
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

from docling.utils.batch_processor import BatchProcessor
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
def temp_dirs(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    return input_dir, output_dir

def test_process_directory_json(mock_converter, temp_dirs):
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
    with pytest.raises(ValueError, match="Unsupported export format"):
        processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            export_format="invalid"
        )

def test_process_directory_conversion_error(mock_converter, temp_dirs):
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
