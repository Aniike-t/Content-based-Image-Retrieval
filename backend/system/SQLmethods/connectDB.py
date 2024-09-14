import sqlite3

def ConnectDB():
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    return c, conn
    
    
