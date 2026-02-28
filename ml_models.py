import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def run_anomaly_detection(df):
    features = [
        'units_injected_kwh', 'units_billed_kwh',
        'loss_percentage', 'load_factor',
        'temperature_celsius', 'voltage_fluctuation'
    ]

    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(contamination=0.12, random_state=42)
    df['anomaly_score'] = model.fit_predict(X_scaled)
    df['is_suspicious'] = df['anomaly_score'] == -1

    return df


def run_risk_model(df):
    df['high_risk'] = (
        (df['transformer_age_years'] > 20) &
        (df['loss_percentage'] > 20)
    ).astype(int)

    feat_cols = [
        'transformer_age_years', 'load_factor',
        'temperature_celsius', 'loss_percentage',
        'voltage_fluctuation', 'outage_hours_monthly'
    ]

    X = df[feat_cols]
    y = df['high_risk']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    df['failure_risk_score'] = rf.predict_proba(X[feat_cols])[:, 1]
    df['risk_label'] = df['failure_risk_score'].apply(
        lambda x: 'HIGH' if x > 0.7 else ('MEDIUM' if x > 0.4 else 'LOW')
    )

    return df


# ✅ THIS IS THE MISSING FUNCTION — it was not included before
def prepare_data(df):
    df = run_anomaly_detection(df)
    df = run_risk_model(df)
    return df
