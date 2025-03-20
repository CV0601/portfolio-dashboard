from dotenv import load_dotenv
import os
from pathlib import Path
import mysql.connector

def db_connection():
    # load environment variables
    dotenv_path_db = Path(r'C:\Users\caspe\Documents\python projects\tws trading\.env')
    print(dotenv_path_db)
    load_dotenv(dotenv_path=dotenv_path_db)
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host=os.getenv('host_db'),
            user=os.getenv('user_db'),
            password=os.getenv('password_db'),
            database=os.getenv('database_db')
        )
        
        if conn.is_connected():
            print("✅ Successfully connected to the database")
            return conn
    except Exception as e:
        print("❌ Connection failed: ", str(e))
        return None