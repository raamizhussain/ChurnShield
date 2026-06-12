import sys
from sqlalchemy import text
from db_connection import get_db_engine

def build_advanced_warehouse():
    engine = get_db_engine()
    
    queries = [
        """
        DROP TABLE IF EXISTS raw_customer_profiles CASCADE;
        CREATE TABLE raw_customer_profiles (
            customer_id VARCHAR(50),
            signup_date DATE,
            current_tier VARCHAR(50),
            country VARCHAR(10)
        );
        """,
        """
        DROP TABLE IF EXISTS dim_customer_scd2 CASCADE;
        CREATE TABLE dim_customer_scd2 (
            customer_key SERIAL PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            signup_date DATE NOT NULL,
            current_tier VARCHAR(50) NOT NULL,
            country VARCHAR(10) NOT NULL,
            valid_from TIMESTAMP NOT NULL,
            valid_to TIMESTAMP,
            is_current BOOLEAN NOT NULL DEFAULT TRUE
        );
        """,
        """
        DROP TABLE IF EXISTS competitor_market_sentiment CASCADE;
        CREATE TABLE competitor_market_sentiment (
            sentiment_id SERIAL PRIMARY KEY,
            scrape_date DATE NOT NULL,
            competitor_name VARCHAR(100) NOT NULL,
            avg_sentiment_score NUMERIC(4,3) NOT NULL,
            volume_count INT NOT NULL,
            CONSTRAINT unique_competitor_date UNIQUE (scrape_date, competitor_name)
        );
        """,
        """
        DROP TABLE IF EXISTS pipeline_watermarks CASCADE;
        CREATE TABLE pipeline_watermarks (
            pipeline_step VARCHAR(100) PRIMARY KEY,
            last_processed_timestamp TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_scd2_id ON dim_customer_scd2(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_scd2_lookup ON dim_customer_scd2(customer_id, valid_from, valid_to);",
        "INSERT INTO pipeline_watermarks (pipeline_step, last_processed_timestamp) VALUES ('ingest_raw_data', '1970-01-01 00:00:00') ON CONFLICT DO NOTHING;"
    ]
    
    try:
        print("Deploying enterprise SCD Type 2, sentiment, and watermark database tables...")
        with engine.begin() as conn:
            for q in queries:
                conn.execute(text(q))
        print("SUCCESS: Advanced relational warehouse entities successfully deployed.")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize schema extensions: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_advanced_warehouse()