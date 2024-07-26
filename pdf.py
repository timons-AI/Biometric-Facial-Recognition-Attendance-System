import pandas as pd
import tabula
import os
import io

def extract_tables_from_pdf(pdf_path):
    try:
        # Try to read all tables from the PDF
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, encoding='latin-1')
        return tables
    except UnicodeDecodeError:
        print("UnicodeDecodeError encountered. Trying a different approach...")
        # If UnicodeDecodeError occurs, try reading the PDF as bytes and then decode
        with open(pdf_path, 'rb') as file:
            pdf_bytes = file.read()
        tables = tabula.read_pdf(io.BytesIO(pdf_bytes), pages='all', multiple_tables=True, encoding='latin-1')
        return tables

def save_tables_to_excel(tables):
    os.makedirs('extracted_tables', exist_ok=True)
    for i, table in enumerate(tables):
        table_name = f"Table_{i+1}"
        excel_path = os.path.join('extracted_tables', f"{table_name}.xlsx")
        table.to_excel(excel_path, index=False)
        print(f"Excel file created: {excel_path}")

def main():
    pdf_path = 'uganda.pdf'  # Replace with your PDF file path
    
    print("Extracting tables from PDF...")
    try:
        tables = extract_tables_from_pdf(pdf_path)
        print(f"Number of tables extracted: {len(tables)}")
        print("Saving tables to Excel files...")
        save_tables_to_excel(tables)
        print("Process completed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()