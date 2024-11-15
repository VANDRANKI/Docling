from docling import DocumentConverter

source_url = "https://arxiv.org/abs/2302.07732"
output_filename = "output.json"

def fetch_and_convert_to_json(source_url, output_filename="output.json"):
    converter = DocumentConverter()
    
    try:
        result = converter.convert(source_url)
        json_content = result.document.export_to_json()
        
        with open(output_filename, "w", encoding="utf-8") as file:
            json.dump(json_content, file, ensure_ascii=False, indent=4)
        
        print(f"JSON saved to {output_filename}")
    
    except Exception as e:
        print(f"Error: {e}")

fetch_and_convert_to_json(source_url)
