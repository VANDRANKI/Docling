from docling.document_converter import DocumentConverter
from pathlib import Path
import json
import traceback
import sys

def convert_local_pdf_to_json(pdf_path, output_filename="output.json"):
    print(f"Starting conversion of PDF: {pdf_path}")
    print(f"Current working directory: {Path.cwd()}")
    
    # Convert relative path to absolute path
    pdf_path = Path(pdf_path).resolve()
    print(f"Absolute PDF path: {pdf_path}")
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return
        
    converter = DocumentConverter()
    
    try:
        print("Initializing conversion...")
        result = converter.convert_file(pdf_path)
        
        print("Converting to JSON...")
        json_content = result.document.export_to_json()
        
        output_path = Path(output_filename)
        print(f"Saving to output file: {output_path.resolve()}")
        
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(json_content, file, ensure_ascii=False, indent=4)
        
        print(f"JSON successfully saved to {output_path}")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Path to your local PDF file
    pdf_path = "../10.1016j.apsusc.2015.03.170.pdf"
    convert_local_pdf_to_json(pdf_path)
