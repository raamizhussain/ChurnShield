import sys
import datetime
import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

def run_idempotent_scd2_pipeline():
    engine = get_db_engine()
    
    simulation_start = datetime.datetime(2026, 1, 1, 0, 0, 0)
    execution_time = datetime.datetime.now()
    
    try:
        df_raw = pd.read_csv('mock_customer_profiles.csv')
    except FileNotFoundError:
        print("CRITICAL: Source profiles data file 'mock_customer_profiles.csv' missing.")
        sys.exit(1)
        
    print(f"Executing calibrated ingestion layer for {len(df_raw)} records...")
    
    active_profiles_query = """
    SELECT customer_key, customer_id, signup_date, current_tier, country 
    FROM dim_customer_scd2 
    WHERE is_current = TRUE;
    """
    
    insert_new_query = """
    INSERT INTO dim_customer_scd2 (customer_id, signup_date, current_tier, country, valid_from, is_current)
    VALUES (:customer_id, :signup_date, :current_tier, :country, :valid_from, TRUE);
    """
    
    expire_old_query = """
    UPDATE dim_customer_scd2 
    SET valid_to = :valid_to, is_current = FALSE 
    WHERE customer_key = :customer_key;
    """
    
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE dim_customer_scd2 RESTART IDENTITY CASCADE;"))
            
            df_active = pd.read_sql(active_profiles_query, con=conn)
            active_map = df_active.set_index('customer_id').to_dict('index')
            
            new_inserts = []
            expirations = []
            re_inserts = []
            
            for _, row in df_raw.iterrows():
                c_id = str(row['customer_id'])
                raw_tier = str(row['current_tier'])
                raw_country = str(row['country'])
                raw_signup = pd.to_datetime(row['signup_date']).date()
                
                if c_id not in active_map:
                    new_inserts.append({
                        "customer_id": c_id,
                        "signup_date": raw_signup,
                        "current_tier": raw_tier,
                        "country": raw_country,
                        "valid_from": simulation_start
                    })
                else:
                    current_state = active_map[c_id]
                    if current_state['current_tier'] != raw_tier:
                        expirations.append({
                            "customer_key": current_state['customer_key'],
                            "valid_to": execution_time
                        })
                        re_inserts.append({
                            "customer_id": c_id,
                            "signup_date": current_state['signup_date'],
                            "current_tier": raw_tier,
                            "country": raw_country,
                            "valid_from": execution_time
                        })
            
            if new_inserts:
                print(f"Writing {len(new_inserts)} timeline-aligned customer identities...")
                conn.execute(text(insert_new_query), new_inserts)
                
            if expirations:
                print(f"Expiring {len(expirations)} outdated profile tiers...")
                conn.execute(text(expire_old_query), expirations)
                conn.execute(text(insert_new_query), re_inserts)
                
        print("SUCCESS: Ingestion processing closed. Timeline sync complete.")
    except Exception as e:
        print(f"CRITICAL: Idempotent database ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_idempotent_scd2_pipeline()