import sqlite3
import os

def create_database(working_dir : str, db_name : str):
    """
    Check if the SQLite database exists in the given directory.
    If not, create a new database with a 'users' table.
    
    :param working_dir: Path to the working directory
    :param db_name: Name of the database file (e.g., 'my_database.db')
    :return: Connection object to the SQLite database
    """
    db_path = os.path.join(working_dir,db_name)
    db_exists = os.path.exists(db_path)

    conn = sqlite3.connection(db_path)
    cursor = conn.cursor()

    if not db_exists:
        print(f"Database {db_name} not found in {working_dir}, creating a new one...")
        cursor.execute("""
        CREATE TABLE users(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       age INTEGER NOT NULL,
                       )
       """)
    return conn , print(f'The database has been created, it has you can find it under: ',{db_path})