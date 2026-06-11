from sqlalchemy import text
from db_connection import get_db_engine

engine = get_db_engine()

populate_fact_query = """
INSERT INTO fact_customer_activity (customer_key, date_actual, activity_type, daily_value_sum, daily_event_count)
SELECT 
    c.customer_key,
    r.activity_date,
    r.activity_type,
    SUM(r.activity_value) AS daily_value_sum,
    COUNT(*) AS daily_event_count
FROM raw_activity_logs r
JOIN dim_customer c ON r.customer_id = c.customer_id
GROUP BY c.customer_key, r.activity_date, r.activity_type
ON CONFLICT DO NOTHING;
"""

with engine.begin() as conn:
    conn.execute(text(populate_fact_query))
    print("SUCCESS: Consolidated raw logs and populated fact_customer_activity table.")