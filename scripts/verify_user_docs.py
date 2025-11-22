"""
Script to verify extraction of the specific test documents provided by the user.
"""
import asyncio
import os
import sys
from app.services.document_processor import process_documents
from app.services.llm_service import extract_field_from_document

# Add the app directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify_test_docs():
    pdf_path = "/Users/harout/amari-project-to-fork/testDocs/BL-COSU534343282.pdf"
    xlsx_path = "/Users/harout/amari-project-to-fork/testDocs/Demo-Invoice-PackingList_1.xlsx"
    
    print(f"Processing files:\n- {pdf_path}\n- {xlsx_path}\n")
    
    if not os.path.exists(pdf_path) or not os.path.exists(xlsx_path):
        print("Error: Test files not found!")
        return

    # 1. Process documents
    print("Step 1: Processing documents...")
    document_data = process_documents([pdf_path, xlsx_path])
    
    print(f"PDF Text Length: {len(document_data.get('pdf_text', ''))}")
    print(f"XLSX Text Length: {len(document_data.get('xlsx_text', ''))}")
    
    # 2. Extract data using LLM
    print("\nStep 2: Extracting data with LLM...")
    extracted_data = extract_field_from_document(document_data)
    
    print("\n--- Extracted Data ---")
    print(extracted_data)
    print("----------------------")

if __name__ == "__main__":
    verify_test_docs()
