import os
import hashlib
import pandas as pd
from dotenv import load_dotenv
from db_connection import get_db_engine

load_dotenv()
engine = get_db_engine()

df_p = pd.read_csv('mock_customer_profiles.csv')
df_l = pd.read_csv('mock_raw_logs.csv')

print("Generating vectorized deduplication matrix for 3.1M log stream...")
combined_string = (
    df_l['customer_id'].astype(str) + 
    df_l['activity_date'].astype(str) + 
    df_l['activity_type'].astype(str) + 
    df_l['activity_value'].astype(str)
)

df_l['log_hash'] = [hashlib.md5(val.encode('utf-8')).hexdigest() for val in combined_string]

print("Removing duplicate log patterns from memory stream...")
df_l = df_l.drop_duplicates(subset=['log_hash'])

cols = ['log_hash', 'customer_id', 'activity_date', 'activity_type', 'activity_value']
df_l = df_l[cols]

with engine.begin() as conn:
    df_p.to_sql('raw_customer_profiles', con=conn, if_exists='append', index=False)
    print("SUCCESS: Ingested production customer profiles.")
    
    df_l.to_sql(
        'raw_activity_logs', 
        con=conn, 
        if_exists='append', 
        index=False, 
        chunksize=100000
    )
    print(f"SUCCESS: Ingested {len(df_l)} unique records into relational warehouse layers.")