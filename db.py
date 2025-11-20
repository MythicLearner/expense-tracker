import os
import sqlite3

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "expenses.db"))

def get_connection(db_path: str = "expenses.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout = 10.0)
    # optional quality of life add-on, makes asking for data easier and simpler
    conn.row_factory = sqlite3.Row
    # 2 execute commands optional for speed and performance
    conn.execute ( "PRAGMA journal_mode = WAL;")
    conn.execute ( "PRAGMA foreign_keys = ON;")
    return conn



def init_db() -> None:
    conn = get_connection()         # <- reuse the same connection options

    cur = conn.cursor()

    cur.executescript ('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        amount REAL NOT NULL CHECK (amount>0),
        category TEXT NOT NULL,
        note TEXT
    );

    --Optional speed-ups for listing/summary
    CREATE INDEX IF NOT EXISTS idx_expenses_date          ON expenses(date);
    CREATE INDEX IF NOT EXISTS idx_expenses_category_date ON expenses(category, date);
                    
    ''')
    conn.commit()
    conn.close()



