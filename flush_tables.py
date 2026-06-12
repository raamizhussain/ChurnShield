from sqlalchemy import text
from db_connection import get_db_engine

def flush_all_tables():
    engine = get_db_engine()
    flush_query = """
    TRUNCATE TABLE fact_customer_activity CASCADE;
    TRUNCATE TABLE raw_activity_logs CASCADE;
    TRUNCATE TABLE raw_customer_profiles CASCADE;
    TRUNCATE TABLE dim_customer CASCADE;
    """
    with engine.begin() as conn:
        conn.execute(text(flush_query))
    print("SUCCESS: Database tables completely flushed.")