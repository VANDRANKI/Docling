"""
Example script demonstrating batch document processing with Docling.

This example shows various features of the BatchProcessor:
- Processing files in parallel
- Progress tracking
- Error handling
- Support for different file types
- Memory-efficient batch processing
"""
import logging
import os
from pathlib import Path
from typing import Tuple

from docling.utils.batch_processor import BatchProcessor
from docling.document_converter import DocumentConverter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def progress_callback(processed: int, total: int) -> None:
    """Custom progress callback function"""
    percentage = (processed / total) * 100
    logger.info(f"Progress: {percentage:.1f}% ({processed}/{total} files)")

def process_documents(
    input_dir: Path,
    output_dir: Path,
    parallel: bool = False,
    batch_size: int = 10
) -> Tuple[int, int]:
    """
    Process documents with error handling and progress tracking.
    
    Args:
        input_dir: Input directory containing documents
        output_dir: Output directory for processed files
        parallel: Whether to use parallel processing
        batch_size: Number of files to process at once
        
    Returns:
        Tuple of (successful_conversions, failed_conversions)
    """
    try:
        # Create a custom converter with specific options if needed
        converter = DocumentConverter()
        
        # Initialize batch processor with parallel processing and progress tracking
        processor = BatchProcessor(
            converter=converter,
            batch_size=batch_size,
            max_workers=os.cpu_count(),  # Use available CPU cores
            progress_callback=progress_callback
        )
        
        # Add custom metadata
        metadata = {
            "project": "research_papers",
            "processor_version": "1.0.0",
            "parallel_processing": parallel,
            "batch_size": batch_size
        }
        
        # Process all PDF files in the directory
        return processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            file_pattern="*.pdf",  # Process PDF files
            export_format="json",  # Export as JSON
            metadata=metadata,     # Include custom metadata
            parallel=parallel      # Enable/disable parallel processing
        )
        
    except FileNotFoundError:
        logger.error(f"Input directory not found: {input_dir}")
        return 0, 0
    except PermissionError:
        logger.error(f"Permission denied accessing directories")
        return 0, 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 0, 0

def main():
    # Define input/output directories
    input_dir = Path("Research_Papers_PDF_Files")
    output_dir = Path("Research_Papers_JSON_Files")
    
    print("\nProcessing documents in parallel mode...")
    successful, failed = process_documents(
        input_dir=input_dir,
        output_dir=output_dir / "parallel",
        parallel=True,
        batch_size=10
    )
    print(f"Parallel processing complete: {successful} successful, {failed} failed")
    
    print("\nProcessing documents in sequential mode...")
    successful, failed = process_documents(
        input_dir=input_dir,
        output_dir=output_dir / "sequential",
        parallel=False,
        batch_size=5
    )
    print(f"Sequential processing complete: {successful} successful, {failed} failed")
    
    # Example with different file types
    print("\nProcessing Word documents...")
    successful, failed = process_documents(
        input_dir=input_dir,
        output_dir=output_dir / "word",
        file_pattern="*.docx"
    )
    print(f"Word document processing complete: {successful} successful, {failed} failed")

if __name__ == "__main__":
    main()
