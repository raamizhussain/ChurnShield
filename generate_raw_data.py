import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

np.random.seed(42)
num_users = 100
start_date = datetime(2026, 1, 1)

customer_ids = [f"CUST_{i:04d}" for i in range(1, num_users + 1)]
signup_dates = [start_date + timedelta(days=int(np.random.randint(0, 30))) for _ in range(num_users)]
tiers = ['Free', 'Premium', 'Enterprise']
tier_assignments = np.random.choice(tiers, size=num_users, p=[0.5, 0.3, 0.2])

customer_profiles = []
for c_id, s_date, tier in zip(customer_ids, signup_dates, tier_assignments):
    customer_profiles.append({
        'customer_id': c_id,
        'signup_date': s_date.strftime('%Y-%m-%d'),
        'current_tier': tier,
        'country': np.random.choice(['US', 'IN', 'UK', 'CA'])
    })

df_profiles = pd.DataFrame(customer_profiles)
df_profiles.to_csv('mock_customer_profiles.csv', index=False)

activity_types = ['login', 'click', 'support_ticket', 'feature_usage']
activity_records = []

for c_id, s_date in zip(customer_ids, signup_dates):
    total_days = 90
    for day in range(total_days):
        current_day = s_date + timedelta(days=day)
        if current_day > datetime(2026, 4, 1):
            break
            
        num_actions = np.random.randint(0, 10)
        for _ in range(num_actions):
            activity_records.append({
                'customer_id': c_id,
                'activity_date': current_day.strftime('%Y-%m-%d'),
                'activity_type': np.random.choice(activity_types, p=[0.3, 0.5, 0.1, 0.1]),
                'activity_value': float(np.random.randint(1, 5))
            })

df_activities = pd.DataFrame(activity_records)

duplicates = df_activities.sample(frac=0.05, random_state=42)
df_activities_with_dupes = pd.concat([df_activities, duplicates], ignore_index=True)

df_activities_with_dupes.to_csv('mock_raw_logs.csv', index=False)
print("SUCCESS: Generated mock_customer_profiles.csv and mock_raw_logs.csv with duplicates included.")