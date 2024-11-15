from docling.document_converter import DocumentConverter
from docling import document_converter
from pathlib import Path
import sys
import requests
import json

def fetch_and_convert_to_json(source_url, output_filename="output.json"):
    converter = DocumentConverter()
    
    try:
        result = converter.convert(source_url)
        
        json_content = result.document.export_to_json()
        
        output_path = Path(__file__).parent / output_filename
        
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(json_content, file, ensure_ascii=False, indent=4)
        
        print(f"JSON saved to {output_path}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")

source_url = "https://arxiv.org/abs/2302.07732"
fetch_and_convert_to_json(source_url)
