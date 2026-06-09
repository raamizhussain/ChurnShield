import configparser
import pandas as pd
from sqlalchemy import create_engine
from lifelines import CoxPHFitter

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

df_snapshots = pd.read_csv('engineered_features.csv')
df_snapshots = df_snapshots[df_snapshots['tenure_days'] > 0].copy()

df_churned_events = df_snapshots[df_snapshots['target_churned'] == 1].copy()
churned_customers = df_churned_events.sort_values('tenure_days').groupby('customer_id').first().reset_index()
churned_ids = churned_customers['customer_id'].unique()

df_active_customers = df_snapshots[~df_snapshots['customer_id'].isin(churned_ids)].sort_values('tenure_days').groupby('customer_id').last().reset_index()

df_model_data = pd.concat([churned_customers, df_active_customers], ignore_index=True)
df_model_data = df_model_data[['customer_id', 'login_velocity_drop', 'click_velocity_drop', 'tenure_days', 'target_churned']]

print("--- Data Sanity Check ---")
print(f"Total rows        : {len(df_model_data)}")
print(f"Churned events    : {int(df_model_data['target_churned'].sum())}")
print(f"Unique tenures    : {df_model_data['tenure_days'].nunique()}")
print(f"Tenure range      : {df_model_data['tenure_days'].min()} - {df_model_data['tenure_days'].max()} days")

cph = CoxPHFitter(penalizer=0.1)
cph.fit(
    df_model_data.drop(columns=['customer_id']),
    duration_col='tenure_days',
    event_col='target_churned'
)

print("\n--- Model Evaluation Metrics ---")
print(f"Concordance Index (C-index): {cph.concordance_index_:.4f}")

print("\n--- Feature Coefficients ---")
print(cph.summary['coef'])

times = [30, 60, 90]
survival_probabilities = cph.predict_survival_function(df_model_data.drop(columns=['customer_id']), times=times)

df_curves = survival_probabilities.T
df_curves.columns = [f'survival_prob_{t}d' for t in times]
df_curves['customer_id'] = df_model_data['customer_id'].values

for t in times:
    df_curves[f'churn_prob_{t}d'] = 1.0 - df_curves[f'survival_prob_{t}d']

df_curves.to_csv('survival_predictions.csv', index=False)
print("\nSUCCESS: Calculated individual 30/60/90-day churn velocity trajectories -> survival_predictions.csv")