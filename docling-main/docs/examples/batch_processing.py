"""
Example script demonstrating batch document processing with Docling.
"""
import logging
from pathlib import Path

from docling.utils.batch_processor import BatchProcessor
from docling.document_converter import DocumentConverter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Create a custom converter with specific options if needed
    converter = DocumentConverter()
    
    # Initialize batch processor with the converter
    processor = BatchProcessor(converter)
    
    # Define input/output directories
    input_dir = Path("Research_Papers_PDF_Files")
    output_dir = Path("Research_Papers_JSON_Files")
    
    # Add custom metadata if desired
    metadata = {
        "project": "research_papers",
        "processor_version": "1.0.0"
    }
    
    # Process all PDF files in the directory
    successful, failed = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        file_pattern="*.pdf",  # Process PDF files
        export_format="json",  # Export as JSON
        metadata=metadata      # Include custom metadata
    )
    
    print(f"\nBatch processing complete:")
    print(f"Successfully processed: {successful} files")
    print(f"Failed to process: {failed} files")
    print(f"\nOutput files can be found in: {output_dir}")

if __name__ == "__main__":
    main()
