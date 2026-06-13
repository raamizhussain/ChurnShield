import sys
import datetime
import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

def total_warehouse_rebuild():
    engine = get_db_engine()
    print("Initiating clean structural data warehouse rebuild sequence...")
    
    setup_queries = [
        "DROP TABLE IF EXISTS fact_customer_activity CASCADE;",
        "DROP TABLE IF EXISTS dim_customer_scd2 CASCADE;",
        """
        CREATE TABLE dim_customer_scd2 (
            customer_key SERIAL PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            signup_date DATE NOT NULL,
            current_tier VARCHAR(50) NOT NULL,
            country VARCHAR(10) NOT NULL,
            valid_from DATE NOT NULL,
            valid_to DATE,
            is_current BOOLEAN NOT NULL DEFAULT TRUE
        );
        """,
        """
        CREATE TABLE fact_customer_activity (
            activity_id SERIAL PRIMARY KEY,
            customer_key INT NOT NULL,
            customer_id VARCHAR(50) NOT NULL,
            date_actual DATE NOT NULL,
            activity_type VARCHAR(50) NOT NULL,
            daily_event_count INT NOT NULL
        );
        """,
        "CREATE INDEX idx_scd2_id ON dim_customer_scd2(customer_id);",
        "CREATE INDEX idx_scd2_dates ON dim_customer_scd2(customer_id, valid_from, valid_to);",
        "CREATE INDEX idx_fact_lookup ON fact_customer_activity(customer_key, date_actual);"
    ]
    
    with engine.begin() as conn:
        for q in setup_queries:
            conn.execute(text(q))
            
    try:
        df_prof = pd.read_csv('mock_customer_profiles.csv')
        df_logs = pd.read_csv('mock_raw_logs.csv')
    except FileNotFoundError as e:
        print(f"CRITICAL: Required raw source data file missing: {e}")
        sys.exit(1)
        
    print("Populating timeline-aligned SCD Type 2 dimension matrix nodes...")
    df_prof['valid_from'] = datetime.date(2026, 1, 1)
    df_prof['is_current'] = True
    
    with engine.begin() as conn:
        df_prof[['customer_id', 'signup_date', 'current_tier', 'country', 'valid_from', 'is_current']].to_sql(
            'dim_customer_scd2', con=conn, if_exists='append', index=False
        )
        
        print("Extracting generated relational sequence tracking keys...")
        df_db_dims = pd.read_sql("SELECT customer_key, customer_id FROM dim_customer_scd2 WHERE is_current=TRUE;", con=conn)
        key_map = df_db_dims.set_index('customer_id')['customer_key'].to_dict()
        
        print("Removing duplicate patterns and cleaning log stream memory...")
        df_logs = df_logs.drop_duplicates(subset=['customer_id', 'activity_date', 'activity_type']).copy()
        
        print("Mapping customer transactional indices to SCD Type 2 master nodes...")
        df_logs['customer_key'] = df_logs['customer_id'].map(key_map)
        
        df_logs = df_logs.dropna(subset=['customer_key'])
        df_logs['customer_key'] = df_logs['customer_key'].astype(int)
        
        df_logs = df_logs.rename(columns={
            'activity_date': 'date_actual',
            'activity_value': 'daily_event_count'
        })
        
        print(f"Bulk streaming {len(df_logs)} records into database layers...")
        df_logs[['customer_key', 'customer_id', 'date_actual', 'activity_type', 'daily_event_count']].to_sql(
            'fact_customer_activity', con=conn, if_exists='append', index=False, chunksize=100000
        )
        
    print("SUCCESS: Relational warehouse entities rebuilt and synchronized perfectly.")

if __name__ == "__main__":
    total_warehouse_rebuild()