import pandas as pd
import re
import pdfplumber
import ollama
import json

class DataParser:
    def __init__(self):
        # Maps raw headers to internal standard names required by rules.py
        self.column_mapping = {
            'invoice_id': ['invoice_id', 'inv_id', 'id', 'transaction_id'],
            'invoice_number': ['invoice_number', 'inv_no', 'invoice_no', 'reference'],
            'vendor_id': ['vendor_id', 'vendor_code', 'supplier_id'],
            'amount': ['amount', 'total_amount', 'invoice_amt', 'value'],
            'contract_value': ['contract_value', 'po_value', 'agreement_amount', 'contract_limit'],
            'invoice_date': ['invoice_date', 'date_of_invoice', 'document_date'],
            'entry_date': ['entry_date', 'posting_date', 'system_date', 'created_at'],
            'procurement_type': ['procurement_type', 'source_type', 'category'],
            'bank_account_number': ['bank_account_number', 'account_no', 'iban']
        }

    def clean_currency(self, value):
        """Helper to remove symbols like '₹', '$', ',' from strings."""
        if isinstance(value, str):
            clean_str = re.sub(r'[^\d.-]', '', value)
            try:
                return float(clean_str) if clean_str else 0.0
            except ValueError:
                return 0.0
        return value

    def _extract_with_llama(self, raw_text):
        """Sends raw text to Llama 3.2 via Ollama to extract structured JSON data."""
        prompt = f"""
        You are a data extraction assistant. Extract vendor invoice data from the text below.
        Return strictly a JSON ARRAY of objects. Each object must have these keys (if found):
        "invoice_number", "vendor_id", "amount", "contract_value", "invoice_date", "entry_date", "procurement_type", "bank_account_number".
        
        Rules:
        1. If a value is missing, use null.
        2. Convert dates to YYYY-MM-DD format if possible.
        3. Do NOT include any explanation, markdown, or code blocks. Just the raw JSON string.
        
        Text to extract from:
        {raw_text}
        """

        try:
            # Send to local Ollama instance
            response = ollama.chat(model='llama3.2', messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            content = response['message']['content'].strip()
            
            # Clean up potential markdown code blocks (e.g. ```json ... ```)
            if content.startswith("```"):
                content = content.strip("`").replace("json", "").strip()
            
            data = json.loads(content)
            
            # Ensure we always return a list of dicts
            if isinstance(data, dict):
                return [data]
            return data
            
        except Exception as e:
            print(f"Llama extraction error: {e}")
            return []

    def process(self, file_path: str) -> pd.DataFrame:
        """
        Main pipeline: Load -> Standardize Columns -> Clean Data Types -> Fill Missing Columns
        """
        try:
            # 1. Load Data based on file type
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.pdf'):
                all_extracted_data = []
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            page_data = self._extract_with_llama(text)
                            all_extracted_data.extend(page_data)
                df = pd.DataFrame(all_extracted_data)
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Error processing file: {e}")
            return pd.DataFrame()

        if df.empty:
            return df

        # 2. Standardize Columns (Rename extracted columns to standard names)
        # Convert all current columns to lowercase snake_case
        df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]
        
        rename_dict = {}
        for standard, aliases in self.column_mapping.items():
            for alias in aliases:
                if alias in df.columns:
                    rename_dict[alias] = standard
                    break
        df = df.rename(columns=rename_dict)

        # 3. CRITICAL FIX: Guarantee all required columns exist
        # If a column (like 'contract_value') is missing, create it with a default value.
        for required_col in self.column_mapping.keys():
            if required_col not in df.columns:
                if required_col in ['amount', 'contract_value']:
                    df[required_col] = 25000.0  # Fill missing numbers with 0.0
                else:
                    df[required_col] = None # Fill missing text with None

        # 4. Clean Data Types
        # Clean currency columns
        for col in ['amount', 'contract_value']:
            df[col] = df[col].apply(self.clean_currency)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # Clean date columns
        for col in ['invoice_date', 'entry_date']:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean text columns
        text_cols = ['vendor_id', 'invoice_number', 'procurement_type', 'bank_account_number']
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()

        return df