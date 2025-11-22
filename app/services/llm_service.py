from openai import OpenAI
from app.core.config import settings
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_extracted_data(data):
    if not data or "error" in data:
        return data
    
    formatted = data.copy()
    
    if formatted.get("average_price") is not None:
        try:
            price = float(formatted["average_price"])
            formatted["average_price"] = f"${price:.2f}"
        except (ValueError, TypeError):
            pass
    
    if formatted.get("average_gross_weight") is not None:
        try:
            weight = float(formatted["average_gross_weight"])
            formatted["average_gross_weight"] = f"{weight:.2f} kg"
        except (ValueError, TypeError):
            pass
    
    return formatted

EXTRACTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "document_extraction",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "bill_of_lading_number": {
                    "type": ["string", "null"],
                    "description": "The bill of lading number from the document"
                },
                "container_number": {
                    "type": ["string", "null"],
                    "description": "The container number from the document"
                },
                "consignee_name": {
                    "type": ["string", "null"],
                    "description": "The name of the consignee"
                },
                "consignee_address": {
                    "type": ["string", "null"],
                    "description": "The address of the consignee"
                },
                "date_of_export": {
                    "type": ["string", "null"],
                    "description": "The date of export in YYYY-MM-DD format"
                },
                "date": {
                    "type": ["string", "null"],
                    "description": "The general date from the document in YYYY-MM-DD format"
                },
                "line_items_count": {
                    "type": ["integer", "null"],
                    "description": "The total number of line items"
                },
                "average_gross_weight": {
                    "type": ["number", "null"],
                    "description": "The average gross weight across all items in kilograms"
                },
                "average_price": {
                    "type": ["number", "null"],
                    "description": "The average price across all items in USD"
                }
            },
            "required": [
                "bill_of_lading_number",
                "container_number",
                "consignee_name",
                "consignee_address",
                "date_of_export",
                "date",
                "line_items_count",
                "average_gross_weight",
                "average_price"
            ],
            "additionalProperties": False
        }
    }
}

def extract_from_images(pdf_images):
    if not pdf_images:
        return None
    
    print(f"DEBUG: Extracting from {len(pdf_images)} images using Vision API")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts structured data from document images."},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Extract the following fields from the provided document images:

    - Bill of lading number (may appear as "Bill of lading NO" in the document)
    - Container Number
    - Consignee Name
    - Consignee Address
    - Date of export (format as YYYY-MM-DD)
    - Date (format as YYYY-MM-DD)
    - Line Items Count (as an integer)
    - Average Gross Weight (as a number in kilograms, extract numeric value only)
    - Average Price (as a number in USD, extract numeric value only)

    If a field cannot be found, set it to null."""
                }
            ]
        }
    ]
    
    for img_base64 in pdf_images:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_base64}"
            }
        })
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            response_format=EXTRACTION_SCHEMA,
        )
        
        extracted_data = json.loads(response.choices[0].message.content)
        print(f"DEBUG: Vision API extracted data: {extracted_data}")
        formatted_data = format_extracted_data(extracted_data)
        return formatted_data
        
    except Exception as e:
        print(f"DEBUG: Vision API Error: {str(e)}")
        return {"error": str(e)}

def extract_field_from_document(document_data):
    print(f"DEBUG: Received document_data: {document_data}")
    print(f"DEBUG: document_data keys: {document_data.keys() if document_data else 'None'}")
    
    document_text = ""
    if 'pdf_text' in document_data:
        pdf_text = document_data['pdf_text']
        print(f"DEBUG: PDF text length: {len(pdf_text)}")
        print(f"DEBUG: PDF text preview: {pdf_text[:200] if pdf_text else 'EMPTY'}")
        document_text += f"PDF Content:\n{pdf_text}\n\n"
    if 'xlsx_text' in document_data:
        xlsx_text = document_data['xlsx_text']
        print(f"DEBUG: XLSX text length: {len(xlsx_text)}")
        print(f"DEBUG: XLSX text preview: {xlsx_text[:200] if xlsx_text else 'EMPTY'}")
        document_text += f"Excel Content:\n{xlsx_text}\n\n"
    
    print(f"DEBUG: Final document_text length: {len(document_text)}")
    
    if not document_text.strip():
        return {"error": "No text could be extracted from the uploaded documents. Please ensure the files are valid PDFs or Excel files with readable content."}

    prompt = f"""Extract the following fields from the provided documents:

    - Bill of lading number (may appear as "Bill of lading NO" in the document)
    - Container Number
    - Consignee Name
    - Consignee Address
    - Date of export (format as YYYY-MM-DD)
    - Date (format as YYYY-MM-DD)
    - Line Items Count (as an integer)
    - Average Gross Weight (as a number in kilograms, extract numeric value only)
    - Average Price (as a number in USD, extract numeric value only)

    If a field cannot be found, set it to null.

    Documents:
    {document_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from documents."},
                {"role": "user", "content": prompt}
            ],
            response_format=EXTRACTION_SCHEMA,
        )
        
        extracted_data = json.loads(response.choices[0].message.content)
        print(f"DEBUG: Text-based extracted data: {extracted_data}")
        
        formatted_text_data = format_extracted_data(extracted_data)
        result = {"text_extraction": formatted_text_data}
        
        if 'pdf_images' in document_data:
            vision_data = extract_from_images(document_data['pdf_images'])
            if vision_data:
                result["vision_extraction"] = vision_data
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON Parse Error: {str(e)}")
        print(f"DEBUG: Raw response: {response.choices[0].message.content}")
        return {"error": f"Failed to parse JSON response: {str(e)}"}
    except Exception as e:
        print(f"DEBUG: LLM Error: {str(e)}")
        return {"error": str(e)}
