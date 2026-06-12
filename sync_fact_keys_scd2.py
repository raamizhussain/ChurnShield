import sys
import pandas as pd
from sqlalchemy import text
from db_connection import get_db_engine

def run_fact_table_relink():
    engine = get_db_engine()
    
    try:
        df_profiles = pd.read_csv('mock_customer_profiles.csv')
    except FileNotFoundError:
        print("CRITICAL: Source reference file 'mock_customer_profiles.csv' is missing.")
        sys.exit(1)
        
    print("Extracting current SCD Type 2 dimension sequence mappings...")
    dim_query = "SELECT customer_key, customer_id FROM dim_customer_scd2 WHERE is_current = TRUE;"
    
    update_fact_query = """
    UPDATE fact_customer_activity 
    SET customer_key = :customer_key 
    WHERE customer_key = :old_index_placeholder;
    """
    
    try:
        with engine.begin() as conn:
            df_db_dims = pd.read_sql(dim_query, con=conn)
            
            id_to_new_key = df_db_dims.set_index('customer_id')['customer_key'].to_dict()
            
            print("Mapping original tracking indices to updated database sequence keys...")
            total_updated_rows = 0
            
            for old_idx, row in df_profiles.iterrows():
                c_id = str(row['customer_id'])
                old_key_val = old_idx + 1
                
                if c_id in id_to_new_key:
                    new_key_val = id_to_new_key[c_id]
                    
                    if old_key_val != new_key_val:
                        result = conn.execute(
                            text(update_fact_query),
                            {
                                "customer_key": new_key_val,
                                "old_index_placeholder": old_key_val
                            }
                        )
                        total_updated_rows += result.rowcount
                        
            print(f"SUCCESS: Synchronized warehouse references. Modified {total_updated_rows} transaction lines.")
    except Exception as e:
        print(f"CRITICAL: Failed to relink transactional fact matrix references: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_fact_table_relink()