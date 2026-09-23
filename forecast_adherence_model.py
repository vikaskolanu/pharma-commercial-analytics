"""
Pharma Commercial Analytics & Rx Forecasting Platform
Part 2: Time-Series Demand Forecasting & Patient Adherence Risk Classifier

Features:
1. Multi-horizon Demand Forecasting (12 months ahead) on TRx/NRx with WAPE & R2 metrics.
2. Patient Refill Lapse Risk Classification (PDC < 0.80) with ROC-AUC, F1, and Feature Importance.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import roc_auc_score, classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def calculate_wape(actual, predicted):
    """Calculates Weighted Absolute Percentage Error (standard commercial biopharma metric)."""
    return np.sum(np.abs(actual - predicted)) / np.sum(actual) * 100.0


def run_demand_forecasting():
    """Trains a demand forecasting model for 12-month forward commercial TRx volume."""
    print("\n=============================================")
    print(" 1. COMMERCIAL DEMAND FORECASTING (TRx)")
    print("=============================================")

    fact_file = os.path.join(DATA_DIR, "fact_monthly_prescriptions.csv")
    df = pd.read_csv(fact_file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Product_ID", "Territory_ID", "Date"]).reset_index(drop=True)

    # Feature Engineering for Time Series
    df["Month_Num"] = df["Date"].dt.month
    df["Year_Num"] = df["Date"].dt.year
    df["Lag_1_TRx"] = df.groupby(["Product_ID", "Territory_ID"])["TRx_Count"].shift(1)
    df["Lag_2_TRx"] = df.groupby(["Product_ID", "Territory_ID"])["TRx_Count"].shift(2)
    df["Rolling_3M_Mean"] = df.groupby(["Product_ID", "Territory_ID"])["TRx_Count"].transform(lambda x: x.shift(1).rolling(3).mean())

    # Drop early null lags
    df_model = df.dropna().copy()

    # One-hot encode categorical features
    df_encoded = pd.get_dummies(df_model, columns=["Product_ID", "Territory_ID"], drop_first=False)

    feature_cols = [c for c in df_encoded.columns if c not in ["Date", "TRx_Count", "NRx_Count", "Refill_Count", "Gross_Sales_USD", "Net_Sales_USD"]]
    X = df_encoded[feature_cols]
    y = df_encoded["TRx_Count"]

    # Temporal Train/Test split: Train on 2023-2024, Test on 2025
    train_mask = df_model["Year_Num"] < 2025
    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]

    model = GradientBoostingRegressor(n_estimators=120, max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    wape = calculate_wape(y_test.values, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"Demand Forecast WAPE (Weighted Absolute % Error): {wape:.2f}%")
    print(f"Demand Forecast R² Score: {r2:.3f}")
    print(f"Demand Forecast RMSE: {rmse:.2f} units")

    # Add predictions to fact table for Power BI comparison
    df_model.loc[~train_mask, "Forecasted_TRx"] = np.round(y_pred).astype(int)
    df_model.loc[train_mask, "Forecasted_TRx"] = df_model.loc[train_mask, "TRx_Count"] # Historical baseline
    df_model["Forecast_Variance"] = df_model["TRx_Count"] - df_model["Forecasted_TRx"]

    output_fact = os.path.join(DATA_DIR, "fact_monthly_prescriptions_with_forecast.csv")
    df_model.to_csv(output_fact, index=False)
    print(f"[✓] Saved updated commercial fact with forecasts: {output_fact}")


def run_adherence_risk_model():
    """Trains a classifier predicting patient 90-day refill lapse / therapy abandonment."""
    print("\n=============================================")
    print(" 2. PATIENT ADHERENCE & REFILL LAPSE RISK")
    print("=============================================")

    patient_file = os.path.join(DATA_DIR, "fact_patient_adherence.csv")
    df = pd.read_csv(patient_file)

    # Encode features
    features = [
        "Age", "Monthly_Copay_USD", "Comorbidity_Score",
        "Prior_Cardio_Event", "PA_Delay_Flag",
        "Copay_Assistance_Enrolled", "Portal_Active"
    ]
    
    X = df[features]
    y = df["Refill_Lapse_Target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    clf.fit(X_train_scaled, y_train)

    y_pred = clf.predict(X_test_scaled)
    y_prob = clf.predict_proba(X_test_scaled)[:, 1]

    roc_auc = roc_auc_score(y_test, y_prob)
    print(f"Patient Adherence Model ROC-AUC: {roc_auc:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Compliant/Adherent", "Refill Lapse"]))

    # Feature Importance
    importances = pd.Series(clf.feature_importances_, index=features).sort_values(ascending=False)
    print("Top Drivers of Patient Therapy Abandonment:")
    for feat, imp in importances.items():
        print(f"  - {feat}: {imp*100:.1f}%")

    # Score all patients with risk probability for Power BI
    df["Predicted_Dropoff_Risk"] = np.round(clf.predict_proba(scaler.transform(X))[:, 1], 3)
    df["Risk_Category"] = pd.cut(
        df["Predicted_Dropoff_Risk"],
        bins=[-0.01, 0.30, 0.70, 1.0],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    )

    output_adherence = os.path.join(DATA_DIR, "fact_patient_adherence_scored.csv")
    df.to_csv(output_adherence, index=False)
    print(f"[✓] Saved scored patient adherence dataset: {output_adherence}")


if __name__ == "__main__":
    run_demand_forecasting()
    run_adherence_risk_model()
