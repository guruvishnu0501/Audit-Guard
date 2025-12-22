import streamlit as st
import pandas as pd
import os
from parse import DataParser
from rules import FraudDetectionRules
from visuals import get_fraud_linkage_graph  # <--- UPDATED IMPORT

st.set_page_config(page_title="AuditGuard", layout="wide")
st.title("🛡️ AuditGuard: Vendor Fraud Detection")

# --- Settings ---
st.sidebar.header("Settings")
limit = st.sidebar.number_input("Approval Limit (₹)", value=50000)
high_val = st.sidebar.number_input("High Value Threshold (₹)", value=1000000)

uploaded_file = st.file_uploader("Upload Invoices (CSV/Excel/PDF)", type=['csv', 'xlsx', 'pdf'])

if uploaded_file:
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 1. Parsing
        st.subheader("1. Data Extraction")
        parser = DataParser()
        with st.spinner("Parsing data..."):
            df = parser.process(temp_path)
        
        if not df.empty:
            st.success(f"Successfully extracted {len(df)} transactions.")
            
            # 2. Analysis
            st.subheader("2. Fraud Analysis")
            with st.spinner("Running rules engine..."):
                engine = FraudDetectionRules(approval_limit=limit, high_value_threshold=high_val)
                result = engine.apply_all_rules(df)
            
            flag_cols = [c for c in result.columns if c.startswith('flag_')]
            suspicious = result[result[flag_cols].any(axis=1)]
            
            # 3. Metrics
            col1, col2 = st.columns(2)
            col1.metric("Total Transactions", len(df))
            col2.metric("Suspicious Transactions", len(suspicious), delta_color="inverse")

            # 4. Suspicious Table
            if not suspicious.empty:
                st.write("### 🚩 Suspicious Transactions Detected")
                display_cols = ['invoice_number', 'vendor_id', 'amount', 'suspicion_reason', 'bank_account_number']
                
                # Highlight logic for table
                st.dataframe(
                    suspicious[display_cols].style.applymap(lambda x: 'color: red', subset=['suspicion_reason'])
                )
                
                # 5. Fraud Linkage Map (The new stylish graph)
                st.write("### 🕸️ Fraud Linkage Map")
                st.write("Visualizing high-risk flows: Invoice → Vendor → Bank/Watchlist")
                
                # Render the Graphviz Chart
                graph = get_fraud_linkage_graph(result)
                st.graphviz_chart(graph, use_container_width=True)
                
            else:
                st.success("No suspicious activity detected.")
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)