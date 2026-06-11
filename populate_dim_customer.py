from sqlalchemy import text
from db_connection import get_db_engine

engine = get_db_engine()

populate_query = """
INSERT INTO dim_customer (customer_id, signup_date, current_tier, country)
SELECT customer_id, signup_date, current_tier, country 
FROM raw_customer_profiles
ON CONFLICT (customer_id) DO UPDATE SET
    current_tier = EXCLUDED.current_tier,
    country = EXCLUDED.country;
"""

with engine.begin() as conn:
    conn.execute(text(populate_query))
    print("SUCCESS: Synced customer profiles into dim_customer.")