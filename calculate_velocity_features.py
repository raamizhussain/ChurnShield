import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

engine = get_db_engine()

advanced_velocity_query = """
WITH daily_spine AS (
    SELECT 
        c.customer_id,
        c.customer_key,
        d.date_actual,
        COALESCE(SUM(CASE WHEN f.activity_type = 'login' THEN f.daily_event_count ELSE 0 END), 0) AS logins,
        COALESCE(SUM(CASE WHEN f.activity_type = 'click' THEN f.daily_event_count ELSE 0 END), 0) AS clicks,
        COALESCE(SUM(CASE WHEN f.activity_type = 'support_ticket' THEN f.daily_event_count ELSE 0 END), 0) AS tickets,
        COALESCE(SUM(CASE WHEN f.activity_type = 'feature_usage' THEN f.daily_event_count ELSE 0 END), 0) AS features
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
        tickets,
        features,
        AVG(logins) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_logins,
        AVG(clicks) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_clicks,
        SUM(tickets) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS rolling_tickets_14d,
        AVG(features) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_features
    FROM daily_spine
),
velocity_lag AS (
    SELECT 
        customer_id,
        customer_key,
        date_actual,
        rolling_logins,
        rolling_clicks,
        rolling_tickets_14d,
        rolling_features,
        LAG(rolling_logins, 7) OVER(PARTITION BY customer_key ORDER BY date_actual) AS lag_logins,
        LAG(rolling_clicks, 7) OVER(PARTITION BY customer_key ORDER BY date_actual) AS lag_clicks,
        LAG(rolling_features, 7) OVER(PARTITION BY customer_key ORDER BY date_actual) AS lag_features,
        MAX(CASE WHEN logins > 0 OR clicks > 0 THEN date_actual END) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS last_active_date
    FROM rolling_metrics
)
SELECT 
    v.customer_id,
    v.date_actual,
    CASE WHEN v.lag_logins = 0 THEN 0 ELSE (v.rolling_logins - v.lag_logins) / v.lag_logins END AS login_velocity_drop,
    CASE WHEN v.lag_clicks = 0 THEN 0 ELSE (v.rolling_clicks - v.lag_clicks) / v.lag_clicks END AS click_velocity_drop,
    CASE WHEN v.lag_features = 0 THEN 0 ELSE (v.rolling_features - v.lag_features) / v.lag_features END AS feature_velocity_drop,
    v.rolling_tickets_14d AS support_friction_score,
    CASE WHEN v.rolling_logins = 0 THEN 0 ELSE v.rolling_clicks / v.rolling_logins END AS click_to_login_ratio,
    COALESCE(EXTRACT(DAY FROM (v.date_actual::timestamp - v.last_active_date::timestamp)), 0) AS days_since_last_activity,
    EXTRACT(DAY FROM (v.date_actual::timestamp - c.signup_date::timestamp)) AS tenure_days,
    CASE WHEN v.rolling_logins = 0 AND v.rolling_clicks = 0 THEN 1 ELSE 0 END AS target_churned
FROM velocity_lag v
JOIN dim_customer c ON v.customer_key = c.customer_key
ORDER BY v.customer_id, v.date_actual;
"""

print("Executing upgraded SQL feature extraction pipeline...")
df_features = pd.read_sql(advanced_velocity_query, con=engine)
df_features.to_csv('engineered_features.csv', index=False)
print(f"SUCCESS: Engineered advanced metrics matrix. Saved {len(df_features)} snapshots.")