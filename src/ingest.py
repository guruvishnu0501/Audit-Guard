import pandas as pd
import os

class ReferenceLoader:
    def __init__(self, data_dir="../data"):
        # Points to the data folder relative to src
        self.data_dir = data_dir

    def load_watchlist(self):
        """Loads the list of suspicious vendors from CSV."""
        # Construct path to data/watchlist.csv
        path = os.path.join(self.data_dir, "watchlist.csv")
        
        try:
            if os.path.exists(path):
                df = pd.read_csv(path)
                # We assume the column name is 'vendor_id'
                if 'vendor_id' in df.columns:
                    return df['vendor_id'].astype(str).str.strip().tolist()
            
            # If file doesn't exist or column is missing, return empty list
            print(f"Warning: Watchlist not found or invalid at {path}")
            return []
        except Exception as e:
            print(f"Error loading watchlist: {e}")
            return []

    def load_market_rates(self):
        """Loads market rates for comparison (placeholder for future logic)."""
        path = os.path.join(self.data_dir, "market_rates.csv")
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()