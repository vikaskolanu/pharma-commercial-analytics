"""
Pharma Commercial Analytics & Rx Forecasting Platform
Part 1: Data Pipeline & Longitudinal Claims Harmonization

Simulates and harmonizes realistic Medicare Part D / Commercial claims data
following standard healthcare data architectures (Star Schema).
Therapeutic Areas modeled:
- Cardiovascular / Lipid Management (Repatha [Amgen] vs. Praluent [Regeneron/Sanofi] & Statins)
- Bone Health (Prolia/Evenity [Amgen] vs. Forteo & Bisphosphonates)
- Immunology (Enbrel [Amgen] vs. Humira & Stelara)
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime

# Set seed for reproducible commercial data
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def generate_dimension_tables():
    """Generates Dim_Products, Dim_Geography, and Dim_Prescribers."""
    print("[+] Generating Dimension Tables...")

    # 1. Product Dimension
    products = [
        {"Product_ID": "PRD_001", "Brand_Name": "Repatha", "Manufacturer": "Amgen", "Therapy_Area": "Cardiology", "Formulation": "Injectable SubQ", "Launch_Year": 2015, "WAC_Price_Monthly": 585},
        {"Product_ID": "PRD_002", "Brand_Name": "Praluent", "Manufacturer": "Regeneron", "Therapy_Area": "Cardiology", "Formulation": "Injectable SubQ", "Launch_Year": 2015, "WAC_Price_Monthly": 590},
        {"Product_ID": "PRD_003", "Brand_Name": "Generic Atorvastatin", "Manufacturer": "Viatris", "Therapy_Area": "Cardiology", "Formulation": "Oral Tablet", "Launch_Year": 2011, "WAC_Price_Monthly": 15},
        {"Product_ID": "PRD_004", "Brand_Name": "Prolia", "Manufacturer": "Amgen", "Therapy_Area": "Bone Health", "Formulation": "Injectable SubQ", "Launch_Year": 2010, "WAC_Price_Monthly": 1250},
        {"Product_ID": "PRD_005", "Brand_Name": "Evenity", "Manufacturer": "Amgen", "Therapy_Area": "Bone Health", "Formulation": "Injectable SubQ", "Launch_Year": 2019, "WAC_Price_Monthly": 1825},
        {"Product_ID": "PRD_006", "Brand_Name": "Forteo", "Manufacturer": "Eli Lilly", "Therapy_Area": "Bone Health", "Formulation": "Injectable SubQ", "Launch_Year": 2002, "WAC_Price_Monthly": 1950},
        {"Product_ID": "PRD_007", "Brand_Name": "Enbrel", "Manufacturer": "Amgen", "Therapy_Area": "Immunology", "Formulation": "Injectable SubQ", "Launch_Year": 1998, "WAC_Price_Monthly": 3400},
        {"Product_ID": "PRD_008", "Brand_Name": "Humira", "Manufacturer": "AbbVie", "Therapy_Area": "Immunology", "Formulation": "Injectable SubQ", "Launch_Year": 2002, "WAC_Price_Monthly": 3500},
    ]
    df_products = pd.DataFrame(products)
    df_products.to_csv(os.path.join(DATA_DIR, "dim_products.csv"), index=False)

    # 2. Geography / Territory Dimension
    territories = [
        {"Territory_ID": "TER_NE_01", "Region": "Northeast", "State": "NY", "Territory_Name": "Metro New York", "Sales_Director": "Sarah Jenkins"},
        {"Territory_ID": "TER_NE_02", "Region": "Northeast", "State": "MA", "Territory_Name": "Greater Boston", "Sales_Director": "Sarah Jenkins"},
        {"Territory_ID": "TER_MW_01", "Region": "Midwest", "State": "IL", "Territory_Name": "Chicago Area", "Sales_Director": "David Chen"},
        {"Territory_ID": "TER_MW_02", "Region": "Midwest", "State": "OH", "Territory_Name": "Cleveland-Columbus", "Sales_Director": "David Chen"},
        {"Territory_ID": "TER_SO_01", "Region": "South", "State": "TX", "Territory_Name": "Houston-Dallas", "Sales_Director": "Elena Rodriguez"},
        {"Territory_ID": "TER_SO_02", "Region": "South", "State": "FL", "Territory_Name": "Miami-Orlando", "Sales_Director": "Elena Rodriguez"},
        {"Territory_ID": "TER_WE_01", "Region": "West", "State": "CA", "Territory_Name": "Northern California", "Sales_Director": "Marcus Brody"},
        {"Territory_ID": "TER_WE_02", "Region": "West", "State": "CA", "Territory_Name": "Southern California", "Sales_Director": "Marcus Brody"},
    ]
    df_geography = pd.DataFrame(territories)
    df_geography.to_csv(os.path.join(DATA_DIR, "dim_geography.csv"), index=False)

    # 3. Prescribers (HCPs)
    specialties = ["Cardiologist", "Endocrinologist", "Rheumatologist", "Internal Medicine", "Oncologist"]
    specialty_weights = [0.35, 0.25, 0.20, 0.15, 0.05]
    prescribers = []
    
    for i in range(1, 401):
        npi = f"NPI_{1000000000 + i}"
        spec = np.random.choice(specialties, p=specialty_weights)
        terr = np.random.choice(df_geography["Territory_ID"])
        # Prescriber tier / decile distribution (80/20 rule)
        decile = np.random.choice(range(1, 11), p=[0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05, 0.04, 0.02])
        is_key_opinion_leader = np.random.choice([0, 1], p=[0.92, 0.08])
        
        prescribers.append({
            "NPI": npi,
            "Doctor_Name": f"Dr. Provider_{i}",
            "Specialty": spec,
            "Territory_ID": terr,
            "Prescriber_Decile": decile,
            "Is_KOL": is_key_opinion_leader,
            "Affiliated_Hospital_System": f"HealthSystem_{np.random.randint(1, 20)}"
        })
    df_prescribers = pd.DataFrame(prescribers)
    df_prescribers.to_csv(os.path.join(DATA_DIR, "dim_prescribers.csv"), index=False)

    return df_products, df_geography, df_prescribers


def generate_monthly_commercial_fact(df_products, df_geography, df_prescribers):
    """Generates monthly commercial prescription sales (TRx, NRx, Gross Sales, Market Share)."""
    print("[+] Generating Monthly Commercial Fact Table (36 Months: 2023 - 2025)...")
    
    dates = pd.date_range(start="2023-01-01", end="2025-12-01", freq="MS")
    rows = []
    
    for dt in dates:
        month_idx = (dt.year - 2023) * 12 + dt.month
        month_str = dt.strftime("%Y-%m-%d")
        
        for _, prod in df_products.iterrows():
            prod_id = prod["Product_ID"]
            brand = prod["Brand_Name"]
            mfg = prod["Manufacturer"]
            price = prod["WAC_Price_Monthly"]
            
            # Underlying trend + seasonality
            growth_trend = 1.0 + (0.015 * month_idx if mfg == "Amgen" else 0.008 * month_idx)
            seasonality = 1.0 + 0.06 * np.sin(2 * np.pi * dt.month / 12)
            
            for _, terr in df_geography.iterrows():
                terr_id = terr["Territory_ID"]
                
                # Base volume influenced by brand and region
                base_trx = 350 if brand in ["Repatha", "Prolia"] else (180 if brand == "Evenity" else 420)
                if terr["Region"] in ["West", "South"]:
                    base_trx *= 1.25
                
                noise = np.random.normal(1.0, 0.05)
                monthly_trx = int(base_trx * growth_trend * seasonality * noise)
                
                # NRx (New-to-brand prescriptions) is typically 18% - 30% of TRx
                nrx_ratio = np.random.uniform(0.18, 0.32) if mfg == "Amgen" else np.random.uniform(0.14, 0.22)
                monthly_nrx = int(monthly_trx * nrx_ratio)
                refill_rx = monthly_trx - monthly_nrx
                
                gross_sales = monthly_trx * price
                net_sales = gross_sales * (0.68 if mfg == "Amgen" else 0.65) # rebate / gross-to-net discount
                
                # Commercial market metrics
                hcp_calls = np.random.randint(25, 75)
                sample_units_distributed = int(monthly_nrx * np.random.uniform(0.4, 0.8))
                
                rows.append({
                    "Date": month_str,
                    "Year": dt.year,
                    "Month": dt.month,
                    "Product_ID": prod_id,
                    "Territory_ID": terr_id,
                    "TRx_Count": monthly_trx,
                    "NRx_Count": monthly_nrx,
                    "Refill_Count": refill_rx,
                    "Gross_Sales_USD": round(gross_sales, 2),
                    "Net_Sales_USD": round(net_sales, 2),
                    "Sales_Rep_Calls": hcp_calls,
                    "Sample_Units_Distributed": sample_units_distributed
                })
                
    df_fact_monthly = pd.DataFrame(rows)
    df_fact_monthly.to_csv(os.path.join(DATA_DIR, "fact_monthly_prescriptions.csv"), index=False)
    print(f"[✓] fact_monthly_prescriptions.csv generated: {len(df_fact_monthly)} records.")
    return df_fact_monthly


def generate_patient_claims_and_adherence(df_products):
    """Generates longitudinal patient-level claims to compute PDC and adherence risk."""
    print("[+] Generating Longitudinal Patient Claims & Adherence Cohort (10,000 Patients)...")
    
    n_patients = 10000
    amgen_products = df_products[df_products["Manufacturer"] == "Amgen"]["Product_ID"].values
    
    patients = []
    for i in range(1, n_patients + 1):
        pid = f"PAT_{100000 + i}"
        age = np.random.randint(42, 85)
        gender = np.random.choice(["Male", "Female"], p=[0.48, 0.52])
        prod_id = np.random.choice(amgen_products)
        copay_tier = np.random.choice(["Tier 1", "Tier 2", "Tier 3", "Specialty Tier"], p=[0.10, 0.25, 0.35, 0.30])
        monthly_copay = {"Tier 1": 15, "Tier 2": 45, "Tier 3": 95, "Specialty Tier": 220}[copay_tier]
        
        # Risk factors for therapy drop-off
        comorbidity_score = np.random.randint(0, 5) # Charlson Comorbidity Index proxy
        prior_cardio_event = np.random.choice([0, 1], p=[0.70, 0.30])
        prior_authorization_delayed = np.random.choice([0, 1], p=[0.75, 0.25])
        digital_patient_portal_active = np.random.choice([0, 1], p=[0.60, 0.40])
        copay_assistance_enrolled = np.random.choice([0, 1], p=[0.45, 0.55])
        
        # Days covered in a 365-day treatment window
        base_days_covered = 365 - (monthly_copay * 0.4) - (prior_authorization_delayed * 45) + (copay_assistance_enrolled * 40) + (digital_patient_portal_active * 35) - (comorbidity_score * 12)
        base_days_covered = np.clip(base_days_covered + np.random.normal(0, 30), 60, 365)
        
        pdc = round(base_days_covered / 365.0, 3) # Proportion of Days Covered
        # Healthcare standard: PDC >= 0.80 is considered Adherent
        is_adherent = 1 if pdc >= 0.80 else 0
        refill_lapse_90d = 1 if is_adherent == 0 else np.random.choice([0, 1], p=[0.92, 0.08])
        
        patients.append({
            "Patient_ID": pid,
            "Product_ID": prod_id,
            "Age": age,
            "Gender": gender,
            "Copay_Tier": copay_tier,
            "Monthly_Copay_USD": monthly_copay,
            "Comorbidity_Score": comorbidity_score,
            "Prior_Cardio_Event": prior_cardio_event,
            "PA_Delay_Flag": prior_authorization_delayed,
            "Copay_Assistance_Enrolled": copay_assistance_enrolled,
            "Portal_Active": digital_patient_portal_active,
            "Days_Supply_Covered": int(base_days_covered),
            "PDC_Score": pdc,
            "Adherent_Status": "Adherent (PDC >= 0.80)" if is_adherent == 1 else "Non-Adherent (PDC < 0.80)",
            "Refill_Lapse_Target": refill_lapse_90d
        })
        
    df_adherence = pd.DataFrame(patients)
    df_adherence.to_csv(os.path.join(DATA_DIR, "fact_patient_adherence.csv"), index=False)
    print(f"[✓] fact_patient_adherence.csv generated: {len(df_adherence)} patient records.")
    return df_adherence


if __name__ == "__main__":
    df_prod, df_geo, df_hcp = generate_dimension_tables()
    generate_monthly_commercial_fact(df_prod, df_geo, df_hcp)
    generate_patient_claims_and_adherence(df_prod)
    print("\n[SUCCESS] All Star-Schema dimensional datasets generated in /data directory.")
