import configparser
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

populate_query = """
INSERT INTO dim_customer (customer_id, signup_date, current_tier, country)
SELECT customer_id, signup_date, current_tier, country 
FROM raw_customer_profiles
ON CONFLICT (customer_id) DO UPDATE SET
    current_tier = EXCLUDED.current_tier,
    country = EXCLUDED.country;
"""

with engine.begin() as conn:
    result = conn.execute(text(populate_query))
    print(f"SUCCESS: Synced customer profiles into dim_customer.")