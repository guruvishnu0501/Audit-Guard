import pandas as pd
import numpy as np
from ingest import ReferenceLoader

class FraudDetectionRules:
    def __init__(self, approval_limit=50000, high_value_threshold=1000000):
        self.approval_limit = approval_limit
        self.high_value_threshold = high_value_threshold
        
        loader = ReferenceLoader()
        loaded_list = loader.load_watchlist()
        self.vendor_watchlist = loaded_list if loaded_list else ['BAD_VENDOR_01', 'SUSPECT_INC']

    def apply_all_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        # Standardize Dates
        df['invoice_date'] = pd.to_datetime(df['invoice_date'])
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        
        # --- 1. APPLY FLAGS ---
        
        # Rule 1: Duplicate payments
        df['flag_duplicate_payment'] = df.duplicated(subset=['vendor_id', 'amount', 'invoice_date'], keep=False)

        # Rule 2: Invoice > Contract
        if 'contract_value' in df.columns:
            df['flag_invoice_exceeds_contract'] = df['amount'] > df['contract_value']
        else:
            df['flag_invoice_exceeds_contract'] = False

        # Rule 3: Split Structure (Just below limit)
        lower_bound = self.approval_limit * 0.95
        df['flag_split_structure'] = df['amount'].between(lower_bound, self.approval_limit - 0.01)

        # Rule 4: High Value Non-Competitive
        df['flag_high_val_non_comp'] = (
            (df['amount'] > self.high_value_threshold) & 
            (df['procurement_type'] == 'Non-Competitive')
        )

        # Rule 5: Watchlist
        df['flag_watchlist_vendor'] = df['vendor_id'].isin(self.vendor_watchlist)

        # Rule 6: Reused Invoice Number
        df['flag_reused_invoice_num'] = df.duplicated(subset=['vendor_id', 'invoice_number'], keep=False)

        # Rule 7: Backdated
        df['days_diff'] = (df['entry_date'] - df['invoice_date']).dt.days
        df['flag_backdated'] = df['days_diff'] > 30

        # Rule 8: Fiscal Year Spike (March)
        df['flag_fy_end_spike'] = (
            (df['invoice_date'].dt.month == 3) & 
            (df['amount'] > df['amount'].median() * 2)
        )

        # Rule 9: Shared Bank Accounts
        shared_accounts = df.groupby('bank_account_number')['vendor_id'].nunique()
        suspicious_accounts = shared_accounts[shared_accounts > 1].index.tolist()
        df['flag_shared_bank_acct'] = df['bank_account_number'].isin(suspicious_accounts)

        # Rule 10: Excessive Rounding
        df['flag_excessive_rounding'] = (
            ((df['amount'] + 1) % 1000 == 0) | 
            ((df['amount'] + 0.01) % 1000 == 0)
        )

        # --- 2. GENERATE EXPLANATIONS ---
        # We loop through rows to create a readable string for the UI
        explanations = []
        for index, row in df.iterrows():
            reasons = []
            if row['flag_duplicate_payment']: reasons.append("Duplicate Payment")
            if row['flag_invoice_exceeds_contract']: reasons.append(f"Exceeds Contract (Amt: {row['amount']} > Contract: {row.get('contract_value', 0)})")
            if row['flag_split_structure']: reasons.append("Split Invoice (Just below approval limit)")
            if row['flag_high_val_non_comp']: reasons.append("High Value Non-Competitive Award")
            if row['flag_watchlist_vendor']: reasons.append("Vendor is on Watchlist")
            if row['flag_reused_invoice_num']: reasons.append("Invoice Number Reused")
            if row['flag_backdated']: reasons.append(f"Backdated by {row['days_diff']} days")
            if row['flag_fy_end_spike']: reasons.append("Fiscal Year-End Spike")
            if row['flag_shared_bank_acct']: reasons.append(f"Shared Bank Account ({row['bank_account_number']})")
            if row['flag_excessive_rounding']: reasons.append("Excessive Rounding Detected")
            
            explanations.append(", ".join(reasons) if reasons else "Clean")
        
        df['suspicion_reason'] = explanations
        return df

    def get_summary(self, df: pd.DataFrame):
        flag_cols = [col for col in df.columns if col.startswith('flag_')]
        summary = df[flag_cols].sum().sort_values(ascending=False)
        return summary