import configparser
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

flush_query = """
TRUNCATE TABLE fact_customer_activity CASCADE;
TRUNCATE TABLE raw_activity_logs CASCADE;
TRUNCATE TABLE raw_customer_profiles CASCADE;
TRUNCATE TABLE dim_customer CASCADE;
"""

with engine.begin() as conn:
    conn.execute(text(flush_query))

print("SUCCESS: Database tables completely flushed. Ready for fresh data stream extraction.")