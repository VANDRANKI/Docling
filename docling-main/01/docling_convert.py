from docling.document_converter import DocumentConverter
from docling import document_converter
from pathlib import Path
import sys
import requests

def fetch_and_convert(source_url, output_filename="output.md"):
    converter = DocumentConverter()
    
    try:
        result = converter.convert(source_url)
        
        markdown_content = result.document.export_to_markdown()
        
        output_path = Path(__file__).parent / output_filename
        
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(markdown_content)
        
        print(f"Markdown saved to {output_path}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")

source_url = "https://arxiv.org/abs/2302.07732"
fetch_and_convert(source_url)
