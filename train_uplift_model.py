import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor

np.random.seed(42)

df_survival = pd.read_csv('survival_predictions.csv')
df_features = pd.read_csv('engineered_features.csv')

df_static_features = df_features.sort_values('date_actual').groupby('customer_id').last().reset_index()

feature_cols = [
    'login_velocity_drop', 'click_velocity_drop', 'feature_velocity_drop',
    'support_friction_score', 'click_to_login_ratio', 'days_since_last_activity'
]

df_master = pd.merge(
    df_survival[['customer_id', 'churn_prob_30d', 'churn_prob_60d', 'churn_prob_90d', 'survival_prob_30d']], 
    df_static_features[['customer_id'] + feature_cols], 
    on='customer_id'
)

num_customers = len(df_master)
df_master['treatment'] = np.random.choice([0, 1], size=num_customers, p=[0.5, 0.5])

base_retention_prob = df_master['survival_prob_30d']
treatment_effect = np.where(
    (df_master['login_velocity_drop'] < -0.1) & (df_master['treatment'] == 1),
    0.30 * np.abs(df_master['login_velocity_drop']),
    np.where(df_master['treatment'] == 1, 0.05, 0.0)
)

df_master['actual_outcome'] = base_retention_prob + treatment_effect + np.random.normal(0, 0.01, num_customers)
df_master['actual_outcome'] = df_master['actual_outcome'].clip(0.0, 1.0)

X = df_master[feature_cols]
y = df_master['actual_outcome']
w = df_master['treatment']

X_control = X[w == 0]
y_control = y[w == 0]
X_treat = X[w == 1]
y_treat = y[w == 1]

m0 = LGBMRegressor(n_estimators=100, min_child_samples=15, max_depth=4, learning_rate=0.05, random_state=42, verbose=-1)
m0.fit(X_control, y_control)

m1 = LGBMRegressor(n_estimators=100, min_child_samples=15, max_depth=4, learning_rate=0.05, random_state=42, verbose=-1)
m1.fit(X_treat, y_treat)

df_master['uplift_score'] = m1.predict(X) - m0.predict(X)

df_output = df_master[[
    'customer_id', 'churn_prob_30d', 'churn_prob_60d', 'churn_prob_90d',
    'login_velocity_drop', 'click_velocity_drop', 'treatment', 'actual_outcome', 'uplift_score'
]]

df_output.to_csv('causal_uplift_predictions.csv', index=False)
print("--- Advanced Causal Uplift Snapshot ---")
print(df_output[['customer_id', 'churn_prob_30d', 'uplift_score']].head())