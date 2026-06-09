import configparser
import pandas as pd
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

velocity_query = """
WITH daily_spine AS (
    SELECT 
        c.customer_id,
        c.customer_key,
        d.date_actual,
        COALESCE(SUM(CASE WHEN f.activity_type = 'login' THEN f.daily_event_count ELSE 0 END), 0) AS logins,
        COALESCE(SUM(CASE WHEN f.activity_type = 'click' THEN f.daily_event_count ELSE 0 END), 0) AS clicks
    FROM dim_customer c
    CROSS JOIN (SELECT date_actual FROM dim_date WHERE date_actual <= '2026-04-01') d
    LEFT JOIN fact_customer_activity f ON c.customer_key = f.customer_key AND d.date_actual = f.date_actual
    GROUP BY c.customer_id, c.customer_key, d.date_actual
),
rolling_metrics AS (
    SELECT 
        customer_id,
        customer_key,
        date_actual,
        logins,
        clicks,
        AVG(logins) OVER(
            PARTITION BY customer_key 
            ORDER BY date_actual 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_logins_7d,
        AVG(clicks) OVER(
            PARTITION BY customer_key 
            ORDER BY date_actual 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_clicks_7d
    FROM daily_spine
),
velocity_lag AS (
    SELECT 
        customer_id,
        customer_key,
        date_actual,
        rolling_avg_logins_7d,
        rolling_avg_clicks_7d,
        LAG(rolling_avg_logins_7d, 7) OVER(
            PARTITION BY customer_key 
            ORDER BY date_actual
        ) AS baseline_logins_7d_ago,
        LAG(rolling_avg_clicks_7d, 7) OVER(
            PARTITION BY customer_key 
            ORDER BY date_actual
        ) AS baseline_clicks_7d_ago
    FROM rolling_metrics
)
SELECT 
    v.customer_id,
    v.date_actual,
    v.rolling_avg_logins_7d,
    v.rolling_avg_clicks_7d,
    COALESCE(v.rolling_avg_logins_7d - v.baseline_logins_7d_ago, 0) AS login_velocity_drop,
    COALESCE(v.rolling_avg_clicks_7d - v.baseline_clicks_7d_ago, 0) AS click_velocity_drop,
    EXTRACT(DAY FROM (v.date_actual::timestamp - c.signup_date::timestamp)) AS tenure_days,
    CASE WHEN v.rolling_avg_logins_7d = 0 AND v.rolling_avg_clicks_7d = 0 THEN 1 ELSE 0 END AS target_churned
FROM velocity_lag v
JOIN dim_customer c ON v.customer_key = c.customer_key
ORDER BY v.customer_id, v.date_actual;
"""

print("Executing advanced SQL window function pipeline across database clusters...")
df_features = pd.read_sql(velocity_query, con=engine)

df_features.to_csv('engineered_features.csv', index=False)
print(f"SUCCESS: Engineered velocity matrix. Saved {len(df_features)} calculated feature snapshots to engineered_features.csv")