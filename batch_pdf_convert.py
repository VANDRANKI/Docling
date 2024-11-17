from pdfminer.high_level import extract_text
import json
from datetime import datetime
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='pdf_conversion.log'
)

def create_output_directory(output_dir):
    """Create output directory if it doesn't exist"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory verified/created: {output_dir}")

def get_output_filename(pdf_path, output_dir):
    """Generate JSON output filename from PDF filename"""
    pdf_name = Path(pdf_path).stem
    return os.path.join(output_dir, f"{pdf_name}.json")

def extract_pdf_to_json(pdf_path, output_path):
    """Convert a single PDF file to JSON"""
    logging.info(f"Processing PDF: {pdf_path}")
    
    try:
        # Extract text from PDF
        text = extract_text(pdf_path)
        
        if not text:
            logging.warning(f"No text extracted from {pdf_path}")
            return False
            
        logging.info(f"Successfully extracted {len(text)} characters from {pdf_path}")
        
        # Create structured JSON
        document = {
            "metadata": {
                "source_file": os.path.basename(pdf_path),
                "extraction_date": datetime.now().isoformat(),
                "character_count": len(text)
            },
            "content": text
        }
        
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Successfully saved JSON to {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {str(e)}")
        return False

def batch_convert_pdfs(input_dir, output_dir):
    """Convert all PDFs in input directory to JSON files"""
    create_output_directory(output_dir)
    
    # Get list of PDF files
    pdf_files = list(Path(input_dir).glob('*.pdf'))
    total_files = len(pdf_files)
    
    logging.info(f"Found {total_files} PDF files to process")
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        output_path = get_output_filename(pdf_file, output_dir)
        
        if extract_pdf_to_json(str(pdf_file), output_path):
            successful += 1
        else:
            failed += 1
            
        logging.info(f"Progress: {successful + failed}/{total_files} files processed")
    
    return successful, failed

if __name__ == "__main__":
    input_dir = "docling-main/Research_Papers_PDF_Files"
    output_dir = "docling-main/Research_Papers_JSON_Files"
    
    logging.info("Starting batch PDF conversion")
    successful, failed = batch_convert_pdfs(input_dir, output_dir)
    logging.info(f"Conversion complete. Successfully converted: {successful}, Failed: {failed}")
    print(f"Conversion complete. Successfully converted: {successful}, Failed: {failed}")
    print(f"See pdf_conversion.log for detailed information")
