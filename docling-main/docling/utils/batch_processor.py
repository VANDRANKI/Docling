"""
Batch processing utilities for converting multiple documents.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple, Union
from tqdm import tqdm

from ..document_converter import DocumentConverter
from ..datamodel.document import DoclingDocument

logger = logging.getLogger(__name__)

VALID_FORMATS = {"json", "markdown"}

class BatchProcessor:
    """
    A utility class for batch processing multiple documents using Docling.
    """
    
    def __init__(
        self,
        converter: Optional[DocumentConverter] = None,
        batch_size: int = 10,
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        Initialize the batch processor.
        
        Args:
            converter: Optional custom DocumentConverter instance.
                      If not provided, a new one will be created.
            batch_size: Number of files to process at once (default: 10)
            max_workers: Maximum number of worker threads for parallel processing.
                        If None, uses ThreadPoolExecutor default.
            progress_callback: Optional callback function to report progress.
                             Takes (processed_files, total_files) as arguments.
        """
        self.converter = converter or DocumentConverter()
        self.batch_size = max(1, batch_size)
        self.max_workers = max_workers
        self.progress_callback = progress_callback
    
    def process_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        file_pattern: str = "*.pdf",
        export_format: str = "json",
        metadata: Optional[Dict] = None,
        parallel: bool = False
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
        """
        Process all matching documents in a directory.
        
        Args:
            input_dir: Directory containing input documents
            output_dir: Directory for output files
            file_pattern: Glob pattern for matching files (default: "*.pdf")
            export_format: Output format - "json" or "markdown" (default: "json")
            metadata: Optional metadata to include in output
            parallel: Whether to process files in parallel (default: False)
            
        Returns:
            Tuple of (successful_conversions, failed_conversions)
            
        Raises:
            ValueError: If export_format is not supported
            FileNotFoundError: If input_dir doesn't exist
            PermissionError: If lacking permissions for input/output directories
        """
        if export_format not in VALID_FORMATS:
            raise ValueError(f"Unsupported export format: {export_format}. Valid formats: {', '.join(VALID_FORMATS)}")
        
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot create output directory: {output_dir}") from e
        
        files = list(input_path.glob(file_pattern))
        total_files = len(files)
        logger.info(f"Found {total_files} files matching pattern '{file_pattern}'")
        
        if total_files == 0:
            return 0, 0
        
        successful = 0
        failed = 0
        
        # Process files in batches
        with tqdm(total=total_files, desc="Processing files") as pbar:
            if parallel and total_files > 1:
                successful, failed = self._process_parallel(
                    files, output_path, export_format, metadata, pbar
                )
            else:
                successful, failed = self._process_sequential(
                    files, output_path, export_format, metadata, pbar
                )
        
        logger.info(f"Processing complete. Successful: {successful}, Failed: {failed}")
        return successful, failed
    
    def _process_sequential(
        self,
        files: list,
        output_path: Path,
        export_format: str,
        metadata: Optional[Dict],
        pbar: Optional[tqdm] = None
    ) -> Tuple[int, int]:
        """Process files sequentially"""
        successful = failed = 0
        
        for i, file in enumerate(files):
            try:
                self._process_single_file(file, output_path, export_format, metadata)
                successful += 1
            except Exception as e:
                failed += 1
                logger.error(f"Failed to process {file.name}: {str(e)}")
            
            if pbar:
                pbar.update(1)
            if self.progress_callback:
                self.progress_callback(i + 1, len(files))
        
        return successful, failed
    
    def _process_parallel(
        self,
        files: list,
        output_path: Path,
        export_format: str,
        metadata: Optional[Dict],
        pbar: Optional[tqdm] = None
    ) -> Tuple[int, int]:
        """Process files in parallel using ThreadPoolExecutor"""
        successful = failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._process_single_file,
                    file,
                    output_path,
                    export_format,
                    metadata
                ): file
                for file in files
            }
            
            for future in as_completed(futures):
                try:
                    future.result()
                    successful += 1
                except Exception as e:
                    failed += 1
                    file = futures[future]
                    logger.error(f"Failed to process {file.name}: {str(e)}")
                
                if pbar:
                    pbar.update(1)
                if self.progress_callback:
                    self.progress_callback(successful + failed, len(files))
        
        return successful, failed
    
    def _process_single_file(
        self,
        file: Path,
        output_path: Path,
        export_format: str,
        metadata: Optional[Dict]
    ) -> None:
        """Process a single file"""
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
            else:  # markdown
                self._export_markdown(doc, output_file)
                
            logger.info(f"Successfully processed {file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {file.name}: {str(e)}")
            raise
    
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
