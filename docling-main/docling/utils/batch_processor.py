"""
Batch processing utilities for converting multiple documents.
"""
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..document_converter import DocumentConverter
from ..datamodel.document import DoclingDocument

logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    A utility class for batch processing multiple documents using Docling.
    """
    
    def __init__(self, converter: Optional[DocumentConverter] = None):
        """
        Initialize the batch processor.
        
        Args:
            converter: Optional custom DocumentConverter instance.
                      If not provided, a new one will be created.
        """
        self.converter = converter or DocumentConverter()
    
    def process_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        file_pattern: str = "*.pdf",
        export_format: str = "json",
        metadata: Optional[Dict] = None
    ) -> Tuple[int, int]:
        """
        Process all matching documents in a directory.
        
        Args:
            input_dir: Directory containing input documents
            output_dir: Directory for output files
            file_pattern: Glob pattern for matching files (default: "*.pdf")
            export_format: Output format - "json" or "markdown" (default: "json")
            metadata: Optional metadata to include in output
            
        Returns:
            Tuple of (successful_conversions, failed_conversions)
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = list(input_path.glob(file_pattern))
        logger.info(f"Found {len(files)} files matching pattern '{file_pattern}'")
        
        successful = 0
        failed = 0
        
        for file in files:
            try:
                # Convert document
                result = self.converter.convert(str(file))
                doc = result.document
                
                # Add metadata
                doc_metadata = {
                    "source_file": file.name,
                    "extraction_date": datetime.now().isoformat(),
                    **(metadata or {})
                }
                
                # Export based on format
                output_file = output_path / f"{file.stem}.{export_format}"
                if export_format == "json":
                    self._export_json(doc, doc_metadata, output_file)
                elif export_format == "markdown":
                    self._export_markdown(doc, output_file)
                else:
                    raise ValueError(f"Unsupported export format: {export_format}")
                
                successful += 1
                logger.info(f"Successfully processed {file.name}")
                
            except Exception as e:
                failed += 1
                logger.error(f"Failed to process {file.name}: {str(e)}")
                
            logger.info(f"Progress: {successful + failed}/{len(files)}")
        
        return successful, failed
    
    def _export_json(
        self,
        doc: DoclingDocument,
        metadata: Dict,
        output_file: Path
    ) -> None:
        """Export document as JSON with metadata"""
        data = {
            "metadata": metadata,
            "content": doc.dict()
        }
        output_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def _export_markdown(
        self,
        doc: DoclingDocument,
        output_file: Path
    ) -> None:
        """Export document as Markdown"""
        output_file.write_text(
            doc.export_to_markdown(),
            encoding='utf-8'
        )
