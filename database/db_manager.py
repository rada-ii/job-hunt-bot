import sqlite3
import os
from datetime import datetime


class JobDatabase:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'jobs.db')

    def save_jobs(self, jobs_list):
        """Save scraped jobs to database"""
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


if __name__ == "__main__":
    db = JobDatabase()
    print("Database manager ready")