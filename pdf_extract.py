from pdfminer.high_level import extract_text
import json
from datetime import datetime
import os

def extract_pdf_to_json(pdf_path):
    print(f"Processing PDF: {pdf_path}")
    
    try:
        # Extract text from PDF
        print("Extracting text from PDF...")
        text = extract_text(pdf_path)
        
        if not text:
            print("Warning: No text was extracted from the PDF")
            return
            
        print(f"Successfully extracted {len(text)} characters")
        
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
        output_path = "extracted_content.json"
        print(f"Saving to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved JSON to {output_path}")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    pdf_path = "docling-main/10.1016j.apsusc.2015.03.170.pdf"
    extract_pdf_to_json(pdf_path)
