import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
num_users = 5000
start_date = datetime(2026, 1, 1)
total_days = 90

customer_ids = [f"CUST_{i:05d}" for i in range(1, num_users + 1)]
signup_dates = [start_date + timedelta(days=int(np.random.randint(0, 45))) for _ in range(num_users)]
tiers = ['Free', 'Premium', 'Enterprise']
tier_assignments = np.random.choice(tiers, size=num_users, p=[0.5, 0.3, 0.2])
countries = ['US', 'IN', 'UK', 'CA', 'DE', 'FR', 'JP', 'AU']
country_assignments = np.random.choice(countries, size=num_users)

customer_profiles = []
for c_id, s_date, tier, country in zip(customer_ids, signup_dates, tier_assignments, country_assignments):
    customer_profiles.append({
        'customer_id': c_id,
        'signup_date': s_date.strftime('%Y-%m-%d'),
        'current_tier': tier,
        'country': country
    })

df_profiles = pd.DataFrame(customer_profiles)
df_profiles.to_csv('mock_customer_profiles.csv', index=False)
print(f"SUCCESS: Generated {num_users} production-grade customer profiles.")

activity_types = ['login', 'click', 'support_ticket', 'feature_usage']
activity_p = [0.35, 0.45, 0.10, 0.10]

churn_targets = np.random.choice([True, False], size=num_users, p=[0.30, 0.70])

records = []

for i, (c_id, s_date, tier) in enumerate(zip(customer_ids, signup_dates, tier_assignments)):
    will_churn = churn_targets[i]
    
    if will_churn:
        max_active_days = np.random.randint(15, 75)
    else:
        max_active_days = total_days
        
    base_activity_range = {
        'Free': (1, 6),
        'Premium': (5, 15),
        'Enterprise': (20, 50)
    }[tier]
    
    days_to_simulate = min(total_days, (datetime(2026, 4, 1) - s_date).days)
    if days_to_simulate <= 0:
        continue
        
    for day in range(days_to_simulate):
        if day > max_active_days:
            break
            
        current_day = s_date + timedelta(days=day)
        
        if will_churn:
            if tier == 'Enterprise':
                decay_factor = 1.0 if day < (max_active_days - 10) else 0.1
            else:
                decay_factor = max(0.0, (max_active_days - day) / max_active_days)
        else:
            decay_factor = 1.0 + np.sin(day / 5.0) * 0.15
            
        num_actions = int(np.random.randint(base_activity_range[0], base_activity_range[1] + 1) * decay_factor)
        
        if num_actions == 0:
            continue
            
        for _ in range(num_actions):
            records.append({
                'customer_id': c_id,
                'activity_date': current_day.strftime('%Y-%m-%d'),
                'activity_type': np.random.choice(activity_types, p=activity_p),
                'activity_value': float(np.random.randint(1, 5) if tier == 'Free' else np.random.randint(5, 20))
            })

df_activities = pd.DataFrame(records)
df_activities.to_csv('mock_raw_logs.csv', index=False)
print(f"SUCCESS: Generated {len(df_activities)} streaming transaction log lines.")