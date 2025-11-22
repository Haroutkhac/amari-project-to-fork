"""
Script to generate sample test documents for the document processing application.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import os

def create_sample_pdf():
    """Create a sample Bill of Lading PDF"""
    output_path = "tests/sample_bill_of_lading.pdf"
    os.makedirs("tests", exist_ok=True)
    
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "BILL OF LADING")
    
    # Content
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    content = [
        ("Bill of Lading Number:", "BOL-2024-001234"),
        ("Container Number:", "ABCD1234567"),
        ("Consignee Name:", "ABC Trading Company"),
        ("Consignee Address:", "123 Main Street, New York, NY 10001"),
        ("Date of Export:", "2024-11-15"),
        ("Date:", "2024-11-22"),
    ]
    
    for label, value in content:
        c.drawString(100, y_position, f"{label} {value}")
        y_position -= 30
    
    c.save()
    print(f"Created sample PDF: {output_path}")

def create_sample_xlsx():
    """Create a sample Commercial Invoice and Packing List XLSX"""
    output_path = "tests/sample_invoice.xlsx"
    os.makedirs("tests", exist_ok=True)
    
    # Create a writer object
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # Invoice sheet
        invoice_data = {
            'Item': ['Widget A', 'Widget B', 'Widget C', 'Widget D', 'Widget E'],
            'Quantity': [100, 150, 200, 75, 125],
            'Unit Price': [25.50, 30.00, 15.75, 45.00, 20.25],
            'Gross Weight (kg)': [50, 75, 100, 37.5, 62.5],
        }
        df_invoice = pd.DataFrame(invoice_data)
        df_invoice['Total Price'] = df_invoice['Quantity'] * df_invoice['Unit Price']
        df_invoice.to_excel(writer, sheet_name='Invoice', index=False)
        
        # Summary sheet
        summary_data = {
            'Field': ['Line Items Count', 'Average Gross Weight', 'Average Price'],
            'Value': [len(df_invoice), df_invoice['Gross Weight (kg)'].mean(), df_invoice['Unit Price'].mean()]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"Created sample XLSX: {output_path}")

if __name__ == "__main__":
    create_sample_pdf()
    create_sample_xlsx()
    print("\nSample documents created successfully!")
