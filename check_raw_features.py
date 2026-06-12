import pandas as pd

try:
    df = pd.read_csv('engineered_features_v2.csv')
    
    print("--- General Data Summary ---")
    print(f"Total rows in file: {len(df)}")
    print(f"Total rows where target_churned == 1: {df['target_churned'].sum()}")
    
    print("\n--- Summary Statistics of Velocity Drops ---")
    print(df[['login_velocity_drop', 'click_velocity_drop', 'feature_velocity_drop']].describe())
    
    print("\n--- Inspecting Active Churn Event Snapshots ---")
    churn_rows = df[df['target_churned'] == 1]
    if len(churn_rows) > 0:
        print(churn_rows[['customer_id', 'date_actual', 'login_velocity_drop', 'click_velocity_drop', 'target_churned']].head(15))
    else:
        print("ALERT: No rows found where target_churned == 1. The database query isn't flagging churn events.")
        
except Exception as e:
    print(f"Diagnostic failed: {e}")