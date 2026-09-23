# Pharma Commercial Analytics & Rx Demand Forecasting Platform

An end-to-end pharmaceutical commercial analytics, demand forecasting, and patient adherence risk analysis system built for commercial brand strategy and decision sciences.

## Business Context
In commercial biopharmaceuticals, brand and marketing teams face three critical challenges:
1. **Demand Volatility & Forecasting:** Accurately predicting regional Total Prescriptions (TRx) and New Prescriptions (NRx) to optimize supply chain inventory and sales rep resource allocation.
2. **Patient Drop-off & Non-Adherence:** Identifying early indicators of patient refill lapse (PDC < 0.80) to formulate proactive patient support and adherence programs.
3. **Prescriber Engagement & Market Penetration:** Segmenting Health Care Providers (HCPs) by prescribing volume (Decile analysis) and monitoring brand adoption against competitors across therapeutic areas (e.g., Cardiology, Oncology, Immunology, Bone Health).

## Architecture & Data Flow
```
Longitudinal Rx & Claims Data (CMS Medicare Part D Schema)
                  │
                  ▼
         Data Harmonization & ETL
    (Data Quality, Cleansing, Star Schema)
         /                        \
        ▼                          ▼
Time-Series Demand Forecasting    Patient Adherence Risk Modeling
(XGBoost / Trend Decomp)          (PDC Metric & Refill Lapse Classifier)
        \                          /
         ▼                        ▼
       Structured Commercial Data Warehouse
                  │
                  ▼
       Power BI Commercial Dashboard
 (Market Share, TRx/NRx Trends, Territory Matrix, Adherence Heatmap)
```

## Repository Structure
- `data_pipeline.py`: Ingestion, data hygiene, and creation of dimensional tables (`dim_products`, `dim_prescribers`, `dim_geography`, `fact_monthly_prescriptions`, `fact_patient_adherence`).
- `forecast_adherence_model.py`: Time-series forecasting of drug volumes across territories and machine learning classification for patient adherence risk.
- `export_powerbi_data.py`: Pipeline executor that generates clean CSV datasets ready to be imported directly into Power BI.
- `powerbi/`: Directory containing dashboard guidelines, DAX measures, and data model star-schema definitions.
- `data/`: Exported star-schema datasets.

## Quick Start (Interactive Dashboard)
You can run the end-to-end data pipeline, model training, and launch the interactive web dashboard with:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run data generation and Star-Schema ETL
python data_pipeline.py

# 3. Train Demand Forecasting and Patient Adherence Models
python forecast_adherence_model.py

# 4. Launch Executive Dashboard (Browser)
streamlit run app.py
```
Open `http://localhost:8501` to view the live dashboard.

## Key Metrics & Results
- **Demand Forecasting Accuracy:** Evaluated using Weighted Absolute Percentage Error (**WAPE: 6.36%**) and **R²: 0.868** across 12-month forward projection horizons (Gradient Boosting).
- **Adherence Classification:** Achieved **ROC-AUC of 0.826** predicting patient therapy abandonment within 90 days (Random Forest).
- **Commercial Impact:** Uncovered that out-of-pocket monthly copay (40.7% feature importance) and Prior Authorization delays (16.6%) are the primary drivers of patient drop-off.

