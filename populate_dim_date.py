import configparser
import pandas as pd
from sqlalchemy import create_engine, text

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
engine = create_engine(db_url)

date_range = pd.date_range(start='2026-01-01', end='2026-12-31')

date_records = []
for dt in date_range:
    date_records.append({
        'date_actual': dt.strftime('%Y-%m-%d'),
        'day_name': dt.strftime('%A'),
        'month_actual': int(dt.month),
        'month_name': dt.strftime('%B'),
        'quarter': int((dt.month - 1) // 3 + 1),
        'year_actual': int(dt.year),
        'is_weekend': bool(dt.weekday in [5, 6])
    })

df_date = pd.DataFrame(date_records)

query = """
INSERT INTO dim_date (date_actual, day_name, month_actual, month_name, quarter, year_actual, is_weekend)
VALUES (:date_actual, :day_name, :month_actual, :month_name, :quarter, :year_actual, :is_weekend)
ON CONFLICT (date_actual) DO NOTHING;
"""

with engine.begin() as conn:
    for _, row in df_date.iterrows():
        conn.execute(text(query), {
            'date_actual': row['date_actual'],
            'day_name': row['day_name'],
            'month_actual': row['month_actual'],
            'month_name': row['month_name'],
            'quarter': row['quarter'],
            'year_actual': row['year_actual'],
            'is_weekend': row['is_weekend']
        })

print(f"SUCCESS: Generated and loaded {len(df_date)} calendar days into dim_date.")