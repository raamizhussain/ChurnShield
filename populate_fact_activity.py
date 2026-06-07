import configparser
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

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
    result = conn.execute(text(populate_fact_query))
    print("SUCCESS: Consolidated raw logs and populated fact_customer_activity table.")