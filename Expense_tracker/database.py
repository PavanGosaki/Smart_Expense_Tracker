import sqlite3

def connect():
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        amount REAL,
        category TEXT,
        date TEXT,
        description TEXT
    )
    """)
    
    conn.commit()
    conn.close()

connect()