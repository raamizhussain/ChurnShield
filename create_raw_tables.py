import configparser
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

create_profiles_table = """
CREATE TABLE IF NOT EXISTS raw_customer_profiles (
    customer_id VARCHAR(50) PRIMARY KEY,
    signup_date DATE,
    current_tier VARCHAR(50),
    country VARCHAR(50)
);
"""

create_activities_table = """
CREATE TABLE IF NOT EXISTS raw_activity_logs (
    log_hash VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(50),
    activity_date DATE,
    activity_type VARCHAR(50),
    activity_value NUMERIC
);
"""

with engine.begin() as conn:
    conn.execute(text(create_profiles_table))
    conn.execute(text(create_activities_table))

print("SUCCESS: raw_customer_profiles and raw_activity_logs tables are ready in the database.")