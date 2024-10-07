import sqlite3
import threading

class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()  # Create a lock for thread safety
        self.execute_sql_script()

    def execute_query(self, query, params=()):
        with self.lock:  # Acquire the lock before executing the query
            self.cursor.execute(query, params)
            self.conn.commit()

    def fetch_query_results(self, query, params=()):
        with self.lock:  # Acquire the lock before executing the query
            self.cursor.execute(query, params)
            return self.cursor.fetchall()  # Fetch and return all results

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def execute_sql_script(self):
        # Paths
        database_path = r"D:\Github Local Repos\CBIR\backend\database.db"
        sql_file_path = r"D:\Github Local Repos\CBIR\backend\dbcmd.sql"
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Read and execute the SQL script
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        
        # Execute the SQL commands in the script
        cursor.executescript(sql_script)
        
        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        print("SQL script executed successfully.")


# Usage
def ConnectDB():
    db_manager = DatabaseManager('../database.db')
    return db_manager.cursor, db_manager.conn

def get_db_manager():
    db_manager = DatabaseManager('../database.db')
    return db_manager