from dotenv import load_dotenv
import os
from pathlib import Path
import mysql.connector

def connect_to_db():
    # load environment variables
    dotenv_path_db = Path(r'C:\Users\caspe\Documents\python projects\tws trading\.env')
    load_dotenv(dotenv_path=dotenv_path_db)
    print(os.getenv('host_db'))
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

def disconnect_db(conn, cursor = None):
    
    if cursor and not cursor.closed:
        print("Closing Cursor")
        cursor.close()
        
    if conn.is_connected():
        conn.close()
        print("Closed connection to database")
    else:
        print("Not connected, call 'connect_to_db()' to start a connection.")
        
conn = connect_to_db()
cursor = conn.cursor
disconnect_db(conn)    