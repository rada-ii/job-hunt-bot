import sqlite3
import os

def create_database():
    """Create jobs database table"""
    db_path = os.path.join(os.path.dirname(__file__), 'jobs.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            scraped_date TEXT,
            applied BOOLEAN DEFAULT FALSE
        )
    ''')

    conn.commit()
    conn.close()
    print("Database created successfully")

if __name__ == "__main__":
    create_database()