#!/usr/bin/env python3
"""
Test if PDF is image-based and requires OCR
"""
import sys
import os
import PyPDF2

def analyze_pdf(pdf_path):
    print("=" * 80)
    print("PDF ANALYSIS")
    print("=" * 80)
    
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        
        print(f"\nNumber of pages: {len(reader.pages)}")
        print(f"PDF metadata: {reader.metadata}")
        
        for i, page in enumerate(reader.pages):
            print(f"\n--- Page {i+1} ---")
            text = page.extract_text()
            print(f"Text length: {len(text)}")
            print(f"Text preview: {text[:200] if text else 'EMPTY'}")
            
            # Check if page has images
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].get_object()
                print(f"Number of XObjects (images/forms): {len(xObject)}")
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        print(f"  - Found image: {obj}")
            else:
                print("No XObjects found on this page")

if __name__ == "__main__":
    pdf_path = "/Users/harout/amari-project-to-fork/testDocs/BL-COSU534343282.pdf"
    analyze_pdf(pdf_path)
