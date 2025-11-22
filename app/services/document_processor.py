import os
from app.utils.pdf_utils import extract_text_from_pdf, pdf_to_images_base64

def process_documents(file_paths):
    print(f"DEBUG: Processing {len(file_paths)} files")
    extracted_data = {}
    
    for file_path in file_paths:
        print(f"DEBUG: Processing file: {file_path}")
        print(f"DEBUG: File exists: {os.path.exists(file_path)}")
        
        if file_path.endswith(".pdf"):
            print(f"DEBUG: Processing as PDF")
            pdf_text = extract_text_from_pdf(file_path)
            print(f"DEBUG: Extracted PDF text length: {len(pdf_text)}")
            extracted_data['pdf_text'] = extracted_data.get('pdf_text', "") + "\n" + pdf_text
            
            pdf_images = pdf_to_images_base64(file_path)
            if pdf_images:
                extracted_data['pdf_images'] = pdf_images
                print(f"DEBUG: Converted PDF to {len(pdf_images)} images")
        elif file_path.endswith(".xlsx"):
            print(f"DEBUG: Processing as XLSX")
            import pandas as pd
            try:
                # Read all sheets
                xls = pd.ExcelFile(file_path)
                text_content = []
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    text_content.append(f"Sheet: {sheet_name}\n{df.to_string()}")
                extracted_data['xlsx_text'] = extracted_data.get('xlsx_text', "") + "\n" + "\n".join(text_content)
                print(f"DEBUG: Extracted XLSX text length: {len(extracted_data['xlsx_text'])}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                extracted_data['xlsx_text'] = extracted_data.get('xlsx_text', "") + f"\nError reading {file_path}"
    
    print(f"DEBUG: Final extracted_data keys: {extracted_data.keys()}")
    return extracted_data 