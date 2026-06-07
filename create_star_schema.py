import configparser
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

create_schema_query = """
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE,
    signup_date DATE,
    current_tier VARCHAR(50),
    country VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_actual DATE PRIMARY KEY,
    day_name VARCHAR(10),
    month_actual INT,
    month_name VARCHAR(10),
    quarter INT,
    year_actual INT,
    is_weekend BOOLEAN
);

CREATE TABLE IF NOT EXISTS fact_customer_activity (
    activity_key SERIAL PRIMARY KEY,
    customer_key INT REFERENCES dim_customer(customer_key),
    date_actual DATE REFERENCES dim_date(date_actual),
    activity_type VARCHAR(50),
    daily_value_sum NUMERIC,
    daily_event_count INT
);
"""

with engine.begin() as conn:
    conn.execute(text(create_schema_query))

print("SUCCESS: Analytical Star Schema tables (Dimensions and Facts) generated successfully.")