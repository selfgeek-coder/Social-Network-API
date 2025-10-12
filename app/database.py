import sqlite3
from contextlib import contextmanager

database_name = "database.db"

def init_database():
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL
                       )
        ''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (author_id) REFERENCES users (id)
                )
            ''')

        conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(database_name)
    try:
        yield conn
    finally:
        conn.close()