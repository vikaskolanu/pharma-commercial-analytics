# Biopharmaceutical Commercial Analytics & Decision Sciences Suite

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pharma-commercial-analytics.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end pharmaceutical commercial intelligence and decision sciences platform designed for biopharma brand leadership, sales operations, and market access teams. This system synthesizes multi-year longitudinal prescription claims (Medicare Part D schema) across leading therapeutic franchises, executes supervised machine learning models for 12-month demand forecasting and patient therapy persistence, and delivers an institutional decision-support interface.

---

## Live Application
- **Live Streamlit Deployment:** [https://pharma-commercial-analytics.streamlit.app](https://pharma-commercial-analytics.streamlit.app)
- **Interactive Local Dashboard:** `http://localhost:8501`

---

## Executive Summary & Business Context

In specialty biopharmaceuticals, brand and commercial operations leaders navigate three core strategic challenges:
1. **Demand Volatility & Manufacturing Lead Times:** Biomanufacturing cycles require 9 to 12 months of forward planning. Supply-chain stockouts or surplus inventory lead to patient access crises or multi-million dollar write-downs.
2. **Patient Therapy Discontinuation (Drop-off):** Complex biologic therapies experience high 90-day abandonment rates. Pinpointing whether drop-off stems from out-of-pocket benefit design (copay) or prior authorization (PA) delays enables targeted patient support interventions.
3. **Field Force Execution & Competitive Share of Voice:** Measuring the return on investment of sales representative educational detailing calls and optimizing physician targeting via prescription volume deciles (Pareto 80/20 distribution).

This platform models these dynamics across key biopharmaceutical categories:
- **Cardiovascular / Lipid Management:** Repatha (Amgen) vs. Praluent (Regeneron/Sanofi) & Generic Statins (Viatris).
- **Bone Health / Osteoporosis:** Prolia and Evenity (Amgen) vs. Forteo (Eli Lilly) & Bisphosphonates.
- **Immunology / Autoimmune:** Enbrel (Amgen) vs. Humira (AbbVie).

---

## System Architecture

```
                    Longitudinal Claims & Prescription Data (CMS Part D Schema)
                                               │
                                               ▼
                              Data Harmonization & ETL Engine
                            (Data Quality, Cleaning, Standardization)
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
          Time-Series Demand Forecasting                Patient Persistence Classifier
           (Gradient Boosting Regressor)                  (Random Forest Classifier)
           - Temporal Lag Feature Engineering             - 1-Year PDC Score Calculation
           - Seasonality Decomposition                    - 90-Day Refill Abandonment Risk
           - 12-Month Out-of-Time Horizon                 - Root Cause Feature Attribution
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                             Star-Schema Commercial Data Mart
                  (Fact Monthly Prescriptions, Fact Patient Adherence, Dimensions)
                                               │
                                               ▼
                        Executive Decision Support Application (Streamlit)
               (Overview, Global Map, Competitive Dynamics, Forecast, Field Ops, Adherence)
```

---

## Data Model (Star Schema)

The platform organizes commercial data into a high-performance dimensional schema:
- `fact_monthly_prescriptions_with_forecast.csv` (Primary Fact): 2,304 monthly regional prescription records tracking Total Prescriptions (TRx), New-to-Brand (NRx), Refills, Gross Sales, Net Realized Sales, and ML Model Forecasts.
- `fact_patient_adherence_scored.csv` (Patient Fact): 10,000 longitudinal patient records with out-of-pocket copay tiers, prior authorization delay flags, copay assistance status, calculated PDC scores, and predicted drop-off probabilities.
- `fact_global_commercial_territories.csv`: International sales data across 12 strategic markets (US, Germany, Japan, UK, France, Canada, Italy, Spain, Australia, Brazil, South Korea, Switzerland).
- `dim_products.csv`: Product catalog detailing brand name, manufacturer, therapeutic class, formulation, and wholesale acquisition cost (WAC).
- `dim_geography.csv`: US commercial territory alignment across regions and states.
- `dim_prescribers.csv`: Health Care Provider (HCP) records including specialty, affiliated health system, key opinion leader (KOL) status, and prescribing volume decile (1–10).

---

## Machine Learning Models & Statistical Validation

### 1. 12-Month Commercial Demand Forecasting Engine
- **Objective:** Predict monthly forward Total Prescriptions (TRx) by brand and territory to inform biomanufacturing production quotas and financial guidance.
- **Model Architecture:** Gradient Boosting Regressor (120 estimators, max depth 4) trained on rolling 3-month means, 1-month and 2-month volume lags, seasonality indices, and territory encodings.
- **Validation Methodology:** Strict temporal out-of-time evaluation: trained on 2023–2024 historical records; evaluated against unseen 2025 commercial quarters.
- **Results:**
  - **Weighted Absolute Percentage Error (WAPE):** `6.36%` (Exceeds biopharma planning benchmark of `< 10.0%`).
  - **Variance Explained ($R^2$):** `0.868`
  - **Root Mean Squared Error (RMSE):** `46.11 units / region`

### 2. Patient Adherence & Refill Abandonment Classifier
- **Objective:** Identify patients at high risk of 90-day therapy drop-off to trigger targeted patient support programs (copay cards, nurse navigation).
- **Core Standard:** Calculated the **Proportion of Days Covered (PDC)** over a 365-day treatment window. Patients with $\text{PDC} \ge 0.80$ meet the CMS/FDA clinical compliance standard.
- **Model Architecture:** Random Forest Classifier (150 trees, max depth 6) with stratified 5-fold cross-validation.
- **Results:**
  - **ROC-AUC Score:** `0.826`
  - **Classification Accuracy:** `79.0%` (F1-score: `0.78`)
- **Root Cause Feature Attribution (Gini Importance):**
  1. **Monthly Out-of-Pocket Copay ($):** `40.7%`
  2. **Copay Assistance Enrollment Status:** `18.6%`
  3. **Prior Authorization (PA) Delay Flag:** `16.6%`
  4. **Charlson Comorbidity Burden:** `10.9%`
  5. **Digital Patient Portal Engagement:** `9.9%`
  6. **Patient Demographics (Age):** `2.8%`

---

## Core Findings & Commercial Insights

1. **The Financial Abandonment Barrier:** Out-of-pocket copay tiers above $95/month drive **40.7% of all observed therapy abandonment**. Enrolling vulnerable patients into automated copay assistance programs increases 1-year PDC adherence by **+23.8%**, safeguarding an estimated $36.4M in recurring treatment continuation value.
2. **Competitive Class Positioning:** Within the PCSK9 inhibitor class, **Repatha captured 2.4x the volume of Praluent**, sustained by cardiovascular outcomes trial (CVOT) data. Across all monitored biologic categories, statutory rebates and copay concessions result in an average **32.8% Gross-to-Net (GTN) pricing deduction**.
3. **Field Force Alignment (Pareto 80/20 Rule):** Prescriber deciles 1 through 3 account for **63.8% of total biopharmaceutical prescription volume**. Expanding detailing cadence from 30 to 60 calls in top territories generates a verified **+18.4% lift in new patient starts (NRx)**.

---

## Repository Structure

```
├── app.py                                   # Streamlit executive presentation dashboard
├── data_pipeline.py                         # Data generation, cleaning, and Star-Schema ETL
├── forecast_adherence_model.py              # ML forecasting & patient persistence training
├── requirements.txt                         # Cloud deployment dependencies
├── .streamlit/
│   └── config.toml                          # Pure light theme configuration
├── powerbi/
│   └── POWERBI_GUIDE.md                     # Power BI Star Schema data model & DAX formulas
├── data/
│   ├── fact_monthly_prescriptions_with_forecast.csv
│   ├── fact_patient_adherence_scored.csv
│   ├── fact_global_commercial_territories.csv
│   ├── dim_products.csv
│   ├── dim_geography.csv
│   └── dim_prescribers.csv
└── README.md
```

---

## Installation & Local Execution

### 1. Clone the Repository
```bash
git clone https://github.com/vikaskolanu/pharma-commercial-analytics.git
cd pharma-commercial-analytics
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Pipeline & Train Models
```bash
# Generate Star-Schema datasets
python data_pipeline.py

# Train ML Demand Forecast and Patient Adherence Models
python forecast_adherence_model.py
```

### 4. Launch the Interactive Dashboard
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## Author
**Kolanu Vikas**  
Indian Institute of Technology, Goa  
- **Email:** ikolanuvikas@gmail.com  
- **GitHub:** [vikaskolanu](https://github.com/vikaskolanu)  
- **LinkedIn:** [Kolanu Vikas](https://www.linkedin.com/in/vikaskolanu/)
