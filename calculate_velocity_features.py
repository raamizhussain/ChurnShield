import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

engine = get_db_engine()

advanced_scd2_query = """
WITH daily_spine AS (
    SELECT 
        c.customer_id,
        c.customer_key,
        d.date_actual,
        COALESCE(SUM(CASE WHEN f.activity_type = 'login' THEN f.daily_event_count ELSE 0 END), 0) AS logins,
        COALESCE(SUM(CASE WHEN f.activity_type = 'click' THEN f.daily_event_count ELSE 0 END), 0) AS clicks,
        COALESCE(SUM(CASE WHEN f.activity_type = 'support_ticket' THEN f.daily_event_count ELSE 0 END), 0) AS tickets,
        COALESCE(SUM(CASE WHEN f.activity_type = 'feature_usage' THEN f.daily_event_count ELSE 0 END), 0) AS features
    FROM dim_customer_scd2 c
    CROSS JOIN (SELECT date_actual FROM dim_date WHERE date_actual <= '2026-04-01') d
    LEFT JOIN fact_customer_activity f ON c.customer_key = f.customer_key AND d.date_actual = f.date_actual
    WHERE d.date_actual BETWEEN c.valid_from::date AND COALESCE(c.valid_to::date, '9999-12-31')
    GROUP BY c.customer_id, c.customer_key, d.date_actual
),
rolling_metrics AS (
    SELECT 
        customer_id,
        customer_key,
        date_actual,
        AVG(logins) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS immediate_logins,
        AVG(clicks) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS immediate_clicks,
        AVG(features) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS immediate_features,
        AVG(logins) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS baseline_logins,
        AVG(clicks) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS baseline_clicks,
        AVG(features) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS baseline_features,
        SUM(tickets) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS rolling_tickets_14d,
        MAX(CASE WHEN logins > 0 OR clicks > 0 THEN date_actual END) OVER(PARTITION BY customer_key ORDER BY date_actual ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS last_active_date
    FROM daily_spine
),
market_context AS (
    SELECT 
        scrape_date,
        AVG(avg_sentiment_score) AS market_competitor_sentiment
    FROM competitor_market_sentiment
    GROUP BY scrape_date
)
SELECT 
    v.customer_id,
    v.date_actual,
    CASE 
        WHEN COALESCE(v.baseline_logins, 0) = 0 THEN 0 
        ELSE (v.immediate_logins - v.baseline_logins) / v.baseline_logins 
    END AS login_velocity_drop,
    CASE 
        WHEN COALESCE(v.baseline_clicks, 0) = 0 THEN 0 
        ELSE (v.immediate_clicks - v.baseline_clicks) / v.baseline_clicks 
    END AS click_velocity_drop,
    CASE 
        WHEN COALESCE(v.baseline_features, 0) = 0 THEN 0 
        ELSE (v.immediate_features - v.baseline_features) / v.baseline_features 
    END AS feature_velocity_drop,
    v.rolling_tickets_14d AS support_friction_score,
    CASE 
        WHEN v.immediate_logins = 0 THEN 0 
        ELSE v.immediate_clicks / v.immediate_logins 
    END AS click_to_login_ratio,
    COALESCE(EXTRACT(DAY FROM (v.date_actual::timestamp - v.last_active_date::timestamp)), 0) AS days_since_last_activity,
    COALESCE(m.market_competitor_sentiment, 0.0) AS competitor_macro_sentiment,
    (v.rolling_tickets_14d * COALESCE(m.market_competitor_sentiment, 0.0)) AS market_friction_index,
    EXTRACT(DAY FROM (v.date_actual::timestamp - c.signup_date::timestamp)) AS tenure_days,
    CASE WHEN v.immediate_logins = 0 AND v.immediate_clicks = 0 THEN 1 ELSE 0 END AS target_churned
FROM rolling_metrics v
JOIN dim_customer_scd2 c ON v.customer_key = c.customer_key
LEFT JOIN market_context m ON v.date_actual = m.scrape_date
WHERE v.date_actual BETWEEN c.valid_from::date AND COALESCE(c.valid_to::date, '9999-12-31')
ORDER BY v.customer_id, v.date_actual;
"""

print("Executing upgraded short-vs-long window feature engine across timelines...")
df_features = pd.read_sql(advanced_scd2_query, con=engine)
df_features.to_csv('engineered_features_v2.csv', index=False)
print(f"SUCCESS: Engineered advanced metrics matrix with market context. Saved {len(df_features)} snapshots.")