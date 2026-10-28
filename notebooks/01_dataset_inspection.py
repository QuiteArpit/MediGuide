import os
import pandas as pd
import numpy as np

def inspect_uci_heart():
    print("=" * 60)
    print("1. INSPECTING UCI HEART DISEASE DATASET")
    print("=" * 60)
    
    # UCI Heart Cleveland dataset column names according to heart-disease.names
    columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", 
        "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]
    
    cleveland_path = os.path.join("data", "raw", "uci_heart", "processed.cleveland.data")
    
    if not os.path.exists(cleveland_path):
        print(f"File not found: {cleveland_path}")
        return
        
    df = pd.read_csv(cleveland_path, names=columns, na_values="?")
    
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nData Types & Missing Values:")
    print(df.isna().sum())
    
    print("\nTarget Distribution ('num'):")
    print(df['num'].value_counts().sort_index())
    
    print("\nTarget Binarized (0 = No Heart Disease, 1+ = Presence):")
    binary_target = (df['num'] > 0).astype(int)
    print(binary_target.value_counts())

def inspect_kaggle_symptoms():
    print("\n" + "=" * 60)
    print("2. INSPECTING KAGGLE DISEASE-SYMPTOM DATASET")
    print("=" * 60)
    
    symptoms_path = os.path.join("data", "raw", "kaggle_symptoms", "dataset.csv")
    severity_path = os.path.join("data", "raw", "kaggle_symptoms", "Symptom-severity.csv")
    
    if os.path.exists(symptoms_path):
        df_sym = pd.read_csv(symptoms_path)
        print(f"Dataset Shape: {df_sym.shape[0]} rows, {df_sym.shape[1]} columns")
        
        # Filter for Heart / Cardiovascular diseases in Kaggle dataset
        cvd_diseases = df_sym[df_sym['Disease'].str.contains('Heart|Hypertension', case=False, na=False)]['Disease'].unique()
        print(f"\nCardiovascular-related diseases found: {list(cvd_diseases)}")
    
    if os.path.exists(severity_path):
        df_sev = pd.read_csv(severity_path)
        print(f"\nSeverity Data Shape: {df_sev.shape[0]} rows")
        print("Sample Symptom Severities:")
        print(df_sev.head(10))

if __name__ == "__main__":
    inspect_uci_heart()
    inspect_kaggle_symptoms()