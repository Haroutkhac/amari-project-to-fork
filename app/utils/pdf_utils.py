import PyPDF2
import os
import base64
import io
from typing import Optional, List, Tuple

def pdf_to_images_base64(file_path: str) -> List[str]:
    try:
        from pdf2image import convert_from_path
        
        images = convert_from_path(file_path, dpi=150)
        base64_images = []
        
        for i, image in enumerate(images):
            print(f"DEBUG: Converting page {i+1}/{len(images)} to base64")
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(img_base64)
        
        print(f"DEBUG: Converted {len(base64_images)} pages to base64")
        return base64_images
        
    except ImportError as e:
        print(f"ERROR: pdf2image not installed: {str(e)}")
        return []
    except Exception as e:
        print(f"ERROR: Failed to convert PDF to images: {str(e)}")
        return []

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file. Supports both text-based and image-based PDFs.
    For image-based PDFs, uses OCR (Optical Character Recognition).
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF file
    """
    text = ""
    
    # First, try standard text extraction with PyPDF2
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    # If no text was extracted OR very little text (likely garbage/partial), use OCR
    if len(text.strip()) < 50:
        print(f"DEBUG: extracted text is too short ({len(text.strip())} chars), attempting OCR...")
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import Image
            
            # Convert PDF pages to images
            images = convert_from_path(file_path)
            
            # Perform OCR on each page
            for i, image in enumerate(images):
                print(f"DEBUG: Performing OCR on page {i+1}/{len(images)}")
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
            
            print(f"DEBUG: OCR extracted {len(text)} characters")
            
        except ImportError as e:
            print(f"ERROR: OCR libraries not installed. Install with: pip install pdf2image pytesseract Pillow")
            print(f"ERROR: {str(e)}")
            return ""
        except Exception as e:
            print(f"ERROR: OCR failed: {str(e)}")
            return ""
    
    return text
