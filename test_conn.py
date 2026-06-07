import configparser
from sqlalchemy import create_engine

config = configparser.ConfigParser()
config.read('config.ini')

db_url = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"

try:
    engine = create_engine(db_url)
    connection = engine.connect()
    print("SUCCESS: Connected to ChurnShield Database successfully!")
    connection.close()
except Exception as e:
    print(f"ERROR: Connection failed. Details: {e}")