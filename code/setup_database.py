from dotenv import load_dotenv
import os
from pathlib import Path
import mysql.connector
from logger import logger

def connect_to_db():
    # load environment variables
    dotenv_path_db = Path(r'C:\Users\caspe\Documents\python projects\tws trading\.env')
    load_dotenv(dotenv_path=dotenv_path_db)
    logger.debug(os.getenv('host_db'))
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host=os.getenv('host_db'),
            user=os.getenv('user_db'),
            password=os.getenv('password_db'),
            database=os.getenv('database_db')
        )
        
        if conn.is_connected():
            logger.info("✅ Successfully connected to the database")
            return conn
    except Exception as e:
        logger.exception("❌ Connection failed: %s", str(e))
        return None

def disconnect_db(conn, cursor = None):
    
    if cursor and not cursor.closed:
        logger.info("Closing Cursor")
        cursor.close()
        
    if conn.is_connected():
        conn.close()
        logger.info("Closed connection to database")
    else:
        logger.warning("Not connected, call 'connect_to_db()' to start a connection.")
        
conn = connect_to_db()
cursor = conn.cursor
disconnect_db(conn)