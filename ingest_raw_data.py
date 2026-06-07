import configparser
import hashlib
import pandas as pd
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

def generate_row_hash(row):
    string_to_hash = f"{row['customer_id']}_{row['activity_date']}_{row['activity_type']}_{row['activity_value']}"
    return hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()

def ingest_profiles():
    df = pd.read_csv('mock_customer_profiles.csv')
    
    query = """
    INSERT INTO raw_customer_profiles (customer_id, signup_date, current_tier, country)
    VALUES (:customer_id, :signup_date, :current_tier, :country)
    ON CONFLICT (customer_id) 
    DO UPDATE SET 
        current_tier = EXCLUDED.current_tier,
        country = EXCLUDED.country;
    """
    
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text(query), {
                'customer_id': row['customer_id'],
                'signup_date': row['signup_date'],
                'current_tier': row['current_tier'],
                'country': row['country']
            })
    print(f"SUCCESS: Ingested {len(df)} customer profiles safely.")

def ingest_activities():
    df = pd.read_csv('mock_raw_logs.csv')
    
    df['log_hash'] = df.apply(generate_row_hash, axis=1)
    
    query = """
    INSERT INTO raw_activity_logs (log_hash, customer_id, activity_date, activity_type, activity_value)
    VALUES (:log_hash, :customer_id, :activity_date, :activity_type, :activity_value)
    ON CONFLICT (log_hash) 
    DO NOTHING;
    """
    
    with engine.begin() as conn:
        inserted_counter = 0
        for _, row in df.iterrows():
            result = conn.execute(text(query), {
                'log_hash': row['log_hash'],
                'customer_id': row['customer_id'],
                'activity_date': row['activity_date'],
                'activity_type': row['activity_type'],
                'activity_value': row['activity_value']
            })
            if result.rowcount > 0:
                inserted_counter += 1
                
    print(f"SUCCESS: Processed {len(df)} total source rows. Inserted {inserted_counter} unique records. Safely skipped duplicates.")

if __name__ == "__main__":
    ingest_profiles()
    ingest_activities()