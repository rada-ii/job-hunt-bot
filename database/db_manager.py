import sqlite3
import os
from datetime import datetime


class JobDatabase:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'jobs.db')
        self._init_database()

    def _init_database(self):
        """Initialize database and create table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS jobs
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           title
                           TEXT
                           NOT
                           NULL,
                           company
                           TEXT,
                           location
                           TEXT,
                           scraped_date
                           TEXT,
                           applied
                           BOOLEAN
                           DEFAULT
                           FALSE
                       )
                       ''')
        conn.commit()
        conn.close()

    def save_jobs(self, jobs_list):
        """Save scraped jobs to database"""
        if not jobs_list:
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved_count = 0
        for job in jobs_list:
            # Check if job already exists
            cursor.execute('''
                           SELECT id
                           FROM jobs
                           WHERE title = ?
                             AND company = ?
                           ''', (job['title'], job['company']))

            if not cursor.fetchone():  # Job doesn't exist, save it
                cursor.execute('''
                               INSERT INTO jobs (title, company, location, scraped_date)
                               VALUES (?, ?, ?, ?)
                               ''', (job['title'], job['company'], job['location'],
                                     datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                saved_count += 1

        conn.commit()
        conn.close()
        return saved_count

    def get_all_jobs(self):
        """Get all jobs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM jobs ORDER BY scraped_date DESC')
        jobs = cursor.fetchall()
        conn.close()

        return jobs

    def clear_all_jobs(self):
        """Clear all jobs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM jobs')
        conn.commit()

        # Reset auto-increment counter
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="jobs"')
        conn.commit()
        conn.close()

        print("Database cleared successfully")


if __name__ == "__main__":
    db = JobDatabase()
    print("Database manager ready")