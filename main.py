from scrapers.linkedin_scraper import search_jobs
from database.db_manager import JobDatabase


def main():
    """Main application - scrape and save jobs"""
    print("🤖 JOB HUNT BOT - Starting...")

    # Scrape jobs
    jobs = search_jobs("Python developer", "remote")
    print(f"Scraped {len(jobs)} jobs")

    # Save to database
    db = JobDatabase()
    saved = db.save_jobs(jobs)
    print(f"Saved {saved} new jobs to database")

    # Show all jobs from database
    all_jobs = db.get_all_jobs()
    print(f"\nTotal jobs in database: {len(all_jobs)}")


if __name__ == "__main__":
    main()