import pandas as pd
from parse import DataParser
from rules import FraudDetectionRules

def run_analysis(input_file, output_file):
    print(f"--- Starting Analysis on {input_file} ---")

    # 1. Initialize the Parser and Rules Engine
    parser = DataParser()
    rules_engine = FraudDetectionRules(approval_limit=50000, high_value_threshold=1000000)

    # 2. Process the Data (Clean & Standardize)
    print("Step 1: Parsing and cleaning data...")
    clean_df = parser.process(input_file)

    if clean_df.empty:
        print("Error: No data found or file is empty.")
        return

    # 3. Apply the Fraud Rules
    print("Step 2: Applying fraud detection rules...")
    scored_df = rules_engine.apply_all_rules(clean_df)

    # 4. Generate a Summary
    print("\n--- Flag Summary ---")
    summary = rules_engine.get_summary(scored_df)
    print(summary)

    # 5. Save the detailed report
    print(f"\nStep 3: Saving results to {output_file}...")
    scored_df.to_csv(output_file, index=False)
    print("Done.")

if __name__ == "__main__":
    # Ensure you have a file named 'data.csv' in the same folder, 
    # or change this string to your actual filename.
    INPUT_FILENAME = 'raw_invoices.csv'
    OUTPUT_FILENAME = 'fraud_report.csv'
    
    # Create a dummy file if one doesn't exist so the script runs immediately
    import os
    if not os.path.exists(INPUT_FILENAME):
        print(f"'{INPUT_FILENAME}' not found. Creating dummy data for testing...")
        # Create a tiny CSV just to test the flow
        dummy_data = """invoice_id,invoice_number,vendor_id,amount,invoice_date,entry_date,procurement_type,bank_account_number
1,INV-100,V001,49999,2023-01-01,2023-02-15,Competitive,ACC-123
2,INV-100,V001,49999,2023-01-01,2023-02-15,Competitive,ACC-123
3,INV-102,V002,1500000,2023-03-01,2023-03-02,Non-Competitive,ACC-999
"""
        with open(INPUT_FILENAME, 'w') as f:
            f.write(dummy_data)

    run_analysis(INPUT_FILENAME, OUTPUT_FILENAME)