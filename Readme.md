📊 PJES Data Pipeline & Dashboard

This repository provides an end-to-end ETL pipeline and analytical dashboard for processing and visualizing Extra Duty Security Payment (PJES) data. It ingests multiple Excel files from different units, normalizes job titles and payment rules, and exposes the results through an interactive Streamlit dashboard.

🏗️ Architecture

The project is split into two main components:

ETL & Normalization (Pjes_V3.ipynb)
Python-based data pipeline responsible for data cleaning, regex-based role normalization, and multi-file consolidation.

Interactive Dashboard (app7.py)
Streamlit web application for KPI monitoring, time-series analysis, and interactive data exploration.

🛠️ Features
⚙️ ETL Pipeline

Batch Ingestion: Reads and merges all .xlsx files from a configured directory into a single dataset.

Role Normalization: Expands abbreviations (e.g., "3º SGT", "SD", "DEL") into standardized role names using rule-based mapping and regex.

Business Rule Engine: Automatically assigns quota values (R$ 200 or R$ 300) based on normalized role hierarchy.

Data Quality Checks: Drops records with missing identifiers, handles null values, and removes duplicates.

📈 Analytics Dashboard

Real-Time KPIs:

Total amount paid

Total quotas (split by budget codes 223 and 423)

Number of employees

Average payment per employee

Dynamic Filtering: Filter by fiscal year, month, operational unit, location, and budget code.

Interactive Visualizations:

Top 10 locations by total spend

Monthly payment trends

Spend distribution by role

Data Export: Download filtered datasets and pivot tables to Excel with one click.

🚀 Getting Started
Prerequisites

Python >= 3.10

Dependencies: pandas, numpy, streamlit, plotly, openpyxl

1. Run the ETL

Execute the notebook Pjes_V3.ipynb (or convert it to a .py script) to generate the consolidated dataset:

# The pipeline will scan the configured input directory and output:
PJES_CONSOLIDATED_NORMALIZED.xlsx

2. Run the Dashboard

Once the consolidated file is available (rename it to PJES.xlsx or update the path in the code), start the app:

streamlit run app7.py

📂 Repository Structure
.
├── Pjes_V3.ipynb     # ETL pipeline and regex normalization logic
├── app7.py          # Streamlit dashboard
├── logo_sds.png     # App header branding
├── PJES.xlsx        # Processed dataset (ETL output)
└── README.md

🛡️ Business Rules

Important: The system applies fixed quota values based on role category:

R$ 200.00: Enlisted ranks (Soldier → Sub-Lieutenant), Agents, and Clerks

R$ 300.00: Officers (Aspirant → Colonel), Delegates, Forensic Experts, and Medical Examiners

📌 Notes

The ETL layer is designed to be idempotent: running it multiple times over the same inputs produces consistent outputs.

The dashboard reads directly from the consolidated Excel file and does not modify source data.