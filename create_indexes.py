from sqlalchemy import text
from db_connection import get_db_engine

def apply_performance_indexes():
    engine = get_db_engine()
    
    queries = [
        "CREATE INDEX IF NOT EXISTS idx_raw_logs_cust ON raw_activity_logs(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_raw_logs_date ON raw_activity_logs(activity_date);",
        "CREATE INDEX IF NOT EXISTS idx_dim_cust_id ON dim_customer(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_fact_cust_key ON fact_customer_activity(customer_key);",
        "CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_customer_activity(date_actual);"
    ]
    
    print("Applying B-Tree performance indexes across relational warehouse nodes...")
    with engine.begin() as conn:
        for q in queries:
            conn.execute(text(q))
    print("SUCCESS: Performance indexes applied.")

if __name__ == "__main__":
    apply_performance_indexes()