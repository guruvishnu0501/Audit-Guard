import graphviz

def get_fraud_linkage_graph(df):
    """
    Generates a Graphviz directed graph that mimics the dark-themed
    'Fraud Linkage Map' style provided in the reference image.
    """
    # Initialize Graphviz Digraph
    dot = graphviz.Digraph(comment='Fraud Linkage')
    
    # 1. Global Graph Settings (Dark Theme)
    dot.attr(bgcolor='#0E1117')  # Streamlit Dark Background
    dot.attr(rankdir='LR')       # Left-to-Right Flow
    dot.attr(splines='ortho')    # Orthogonal edges for clean look
    dot.attr(nodesep='0.6')
    
    # 2. Node Defaults
    dot.attr('node', shape='box', style='filled', fontname='Helvetica', fontcolor='white', margin='0.2')
    dot.attr('edge', color='#cccccc', penwidth='1.5', fontname='Helvetica', fontsize='10', fontcolor='#cccccc')

    # 3. Filter for Suspicious Transactions Only
    flag_cols = [c for c in df.columns if c.startswith('flag_')]
    suspicious_df = df[df[flag_cols].any(axis=1)].copy()

    # Limit to top 5 suspicious to keep the graph readable
    if len(suspicious_df) > 5:
        suspicious_df = suspicious_df.head(5)

    for idx, row in suspicious_df.iterrows():
        # --- ID GENERATION ---
        # We use simple strings for IDs in the DOT language
        inv_id = f"inv_{idx}"
        vendor_id = f"vend_{row['vendor_id']}"
        bank_id = f"bank_{row['bank_account_number']}"
        watch_id = f"watch_{row['vendor_id']}"

        # --- NODE 1: INVOICE ("Current Bid") ---
        # Blue, rounded box, File Icon
        label_inv = f"📄 {row['invoice_number']}\n(₹{row['amount']})"
        dot.node(inv_id, label=label_inv, color='#262730', fillcolor='#4B8BBE', shape='note')

        # --- NODE 2: VENDOR ("Fake Construction Ltd") ---
        # Red, rounded box, Building Icon
        label_vend = f"🏢 {row['vendor_id']}"
        dot.node(vendor_id, label=label_vend, color='#262730', fillcolor='#D32F2F', shape='box', style='filled,rounded')

        # --- NODE 3: BANK ACCOUNT ("Acct *9999") ---
        # Brown/Orange, Pill shape, Bank Icon
        label_bank = f"🏦 Acct: {str(row['bank_account_number'])[-4:]}" # Show last 4 digits
        dot.node(bank_id, label=label_bank, color='#262730', fillcolor='#A0522D', shape='oval')

        # --- EDGES ---
        # Invoice -> Vendor
        dot.edge(inv_id, vendor_id, label='Vendor', color='#ff6b6b')

        # Vendor -> Bank
        dot.edge(vendor_id, bank_id, label='Risky Deposit', style='dashed', color='#f0ad4e')

        # --- SPECIAL NODE: WATCHLIST HIT ---
        if row.get('flag_watchlist_vendor', False):
            # Black/Red, Hexagon, Skull Icon
            dot.node(watch_id, label='💀 Watchlist Hit', color='#ff0000', fillcolor='#000000', shape='octagon', fontcolor='#ff0000', penwidth='2.0')
            
            # Vendor -> Watchlist
            dot.edge(vendor_id, watch_id, label='MATCH', style='dotted', color='#ff0000', fontcolor='#ff0000')

        # --- SPECIAL EDGE: SHARED BANK ACCOUNT ---
        # If this vendor shares a bank account flagged by our rules
        if row.get('flag_shared_bank_acct', False):
             # Highlight the bank node as critical
             dot.node(bank_id, color='#ff0000', penwidth='2.0')

    return dot