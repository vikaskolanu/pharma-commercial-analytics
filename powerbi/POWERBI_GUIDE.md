# Power BI Commercial Dashboard Architecture & DAX Measures

This document outlines how to import the data into Power BI, set up the Star Schema relationships, and use the DAX measures.

---

## 1. Data Model (Star Schema)

Import the CSV files located in `data/`:
1. `fact_monthly_prescriptions_with_forecast.csv` (Primary Fact Table)
2. `dim_products.csv` (Product Dimension)
3. `dim_geography.csv` (Geography Dimension)
4. `dim_prescribers.csv` (HCP / Prescriber Dimension)
5. `fact_patient_adherence_scored.csv` (Patient Adherence & Drop-off Risk)

### Relationships (1-to-Many):
- `dim_products[Product_ID]`  ───>  `fact_monthly_prescriptions[Product_ID]`
- `dim_geography[Territory_ID]` ───>  `fact_monthly_prescriptions[Territory_ID]`
- `dim_geography[Territory_ID]` ───>  `dim_prescribers[Territory_ID]`
- `dim_products[Product_ID]`  ───>  `fact_patient_adherence[Product_ID]`

---

## 2. Key DAX Measures for Commercial Analytics

Copy and paste these measures into Power BI:

### A. Total Prescriptions (TRx) & New Prescriptions (NRx)
```dax
Total_TRx = SUM(fact_monthly_prescriptions[TRx_Count])

Total_NRx = SUM(fact_monthly_prescriptions[NRx_Count])

NRx_Conversion_Rate = DIVIDE([Total_NRx], [Total_TRx], 0)
```

### B. Commercial Revenue
```dax
Gross_Revenue_USD = SUM(fact_monthly_prescriptions[Gross_Sales_USD])

Net_Revenue_USD = SUM(fact_monthly_prescriptions[Net_Sales_USD])

Gross_to_Net_Discount_% = DIVIDE([Gross_Revenue_USD] - [Net_Revenue_USD], [Gross_Revenue_USD], 0)
```

### C. Market Share by Therapeutic Area
```dax
Market_TRx_Total = 
CALCULATE(
    [Total_TRx],
    ALLSELECTED(dim_products[Brand_Name])
)

Brand_Market_Share_% = 
DIVIDE([Total_TRx], [Market_TRx_Total], 0)
```

### D. Forecasting Accuracy & Variance
```dax
Forecasted_TRx_Total = SUM(fact_monthly_prescriptions[Forecasted_TRx])

Forecast_Variance = [Total_TRx] - [Forecasted_TRx_Total]

Forecast_Variance_% = DIVIDE([Forecast_Variance], [Total_TRx], 0)
```

### E. Patient Adherence (PDC) & High Risk Patient Count
```dax
Average_PDC = AVERAGE(fact_patient_adherence[PDC_Score])

High_Risk_Dropoff_Count = 
CALCULATE(
    COUNTROWS(fact_patient_adherence),
    fact_patient_adherence[Risk_Category] = "High Risk"
)

Adherence_Rate_% = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_patient_adherence), fact_patient_adherence[Adherent_Status] = "Adherent (PDC >= 0.80)"),
    COUNTROWS(fact_patient_adherence),
    0
)
```

---

## 3. Recommended 3-Page Dashboard Layout

### Page 1: Commercial Brand Performance & Market Dynamics (Executive View)
- **Top KPI Cards:** Total TRx, Total NRx, Net Revenue ($M), Overall Brand Market Share %.
- **Visual 1 (Area Chart):** Monthly TRx Trend by Brand (Repatha vs. Competitors) over time.
- **Visual 2 (Donut Chart):** TRx share by Therapeutic Area (Cardiology, Bone Health, Immunology).
- **Visual 3 (Clustered Bar Chart):** Brand Market Share % across Geographic Regions (West, South, Northeast, Midwest).

### Page 2: Territory Sales Excellence & Forecast Variance (Sales Ops View)
- **Visual 1 (Map / Matrix):** Territory ID, State, Sales Director, Actual TRx vs. Forecasted TRx, Variance %.
- **Visual 2 (Scatter Plot):** Sales Rep Calls (x-axis) vs. NRx Growth (y-axis) with bubble size = Gross Revenue.
- **Visual 3 (Decile Distribution):** Prescriber Deciles 1-10 vs. Total Prescriptions generated (demonstrating 80/20 commercial rule).

### Page 3: Patient Journey & Adherence Drop-off Risk (Decision Sciences View)
- **Top KPI Cards:** Average PDC (0.83), % Adherent Patients, High Risk Patient Count.
- **Visual 1 (Bar Chart):** Drop-off Risk by Copay Tier (Specialty vs. Tier 1-3).
- **Visual 2 (Histogram):** Distribution of Patient PDC Scores with red threshold line at 0.80.
- **Visual 3 (Feature Driver Tree):** Key factors driving therapy non-adherence (Prior Auth Delays, Copay Assistance, Digital Portal usage).
