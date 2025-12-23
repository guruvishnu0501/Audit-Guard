# Audit-Guard
# 🛡️ AuditGuard: AI-Powered Vendor Fraud Detection

**AuditGuard** is an automated forensic auditing system designed to detect vendor fraud, financial anomalies, and collusion risks in real-time. It combines traditional rule-based logic with Generative AI (Llama 3.2) to analyze both structured data (CSV/Excel) and unstructured documents (PDF invoices).

---

## 🚀 Key Features

### 🧠 1. AI-Powered PDF Extraction
Unlike traditional OCR, AuditGuard uses a **Local LLM (Llama 3.2)** to intelligently parse unstructured PDF invoices. It extracts critical fields like *Vendor Name*, *Amount*, and *Bank Account Numbers* regardless of the invoice layout.

### 🕵️ 2. The 10-Point Fraud Framework
Every transaction is screened against a rigorous rules engine:
1.  **Duplicate Payments:** Identical amounts/dates across invoices.
2.  **Structuring (Split Invoices):** Amounts just below approval limits (e.g., ₹49,999).
3.  **Watchlist Hits:** Real-time cross-referencing with blacklisted vendors.
4.  **Collusion Detection:** High-value awards to non-competitive vendors.
5.  **Backdated Invoices:** Significant gaps between invoice date and system entry.
6.  **Excessive Rounding:** Suspicious round numbers (e.g., ₹5,000.00).
7.  **Contract Violations:** Invoice amounts exceeding contract value.
8.  **Fiscal Year Spikes:** Unusual spending patterns in March.
9.  **Shared Bank Accounts:** Multiple vendors using the same bank account.
10. **Reused Invoice Numbers:** Duplicate references for the same vendor.

### 🕸️ 3. Fraud Linkage Map
Visualizes hidden relationships using **Graph Theory**. It generates a directed graph connecting Vendors to Bank Accounts, instantly revealing fraud rings where multiple vendors funnel money to a single destination.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Language:** Python 3.10+
* **AI Model:** Llama 3.2 (via Ollama)
* **Data Processing:** Pandas, NumPy
* **PDF Parsing:** PDFPlumber
* **Visualization:** Graphviz, Streamlit-Graphviz
* **Logic:** Custom Rules Engine

---

## 📂 Project Structure

```text
AuditGuard/
├── data/
│   ├── watchlist.csv          # List of blacklisted vendors
│   └── market_rates.csv       # (Optional) Reference data
├── src/
│   ├── app.py                 # Main Streamlit Application
│   ├── rules.py               # 10-point Fraud Logic Engine
│   ├── parse.py               # Data Ingestion (PDF/CSV) & Llama 3.2 Integration
│   ├── visuals.py             # Graphviz Linkage Map Generator
│   ├── ingest.py              # Helper to load reference data
│   └── main.py                # CLI version of the tool
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```
---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```
git clone [https://github.com/yourusername/AuditGuard.git](https://github.com/yourusername/AuditGuard.git)
cd AuditGuard
```
