import pandas as pd
from lifelines import CoxPHFitter

df_features = pd.read_csv('engineered_features.csv')

df_static = df_features.sort_values('date_actual').groupby('customer_id').last().reset_index()

model_cols = [
    'login_velocity_drop', 
    'click_velocity_drop', 
    'feature_velocity_drop',
    'support_friction_score',
    'click_to_login_ratio',
    'days_since_last_activity',
    'tenure_days', 
    'target_churned'
]
df_model = df_static[model_cols].dropna()

cph = CoxPHFitter(penalizer=0.1)
cph.fit(df_model, duration_col='tenure_days', event_col='target_churned')

print("--- Upgraded Model Evaluation Metrics ---")
print(f"Concordance Index (C-index): {cph.concordance_index_:.4f}")

print("\n--- Feature Impact Weights ---")
print(cph.params_)

df_customers = df_static[['customer_id'] + model_cols[:-2]].copy()
df_customers['churn_prob_30d'] = 1 - cph.predict_survival_function(df_customers, times=[30]).T.iloc[:, 0]
df_customers['churn_prob_60d'] = 1 - cph.predict_survival_function(df_customers, times=[60]).T.iloc[:, 0]
df_customers['churn_prob_90d'] = 1 - cph.predict_survival_function(df_customers, times=[90]).T.iloc[:, 0]
df_customers['survival_prob_30d'] = cph.predict_survival_function(df_customers, times=[30]).T.iloc[:, 0]

df_customers.to_csv('survival_predictions.csv', index=False)
print(f"\nSUCCESS: Calculated trajectories using upgraded feature matrices.")