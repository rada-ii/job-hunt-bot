from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


def setup_browser():
    """Setup Chrome browser in HEADLESS mode - no window opens"""
    chrome_options = Options()

    # HEADLESS MODE - browser runs in background
    chrome_options.add_argument("--headless")  # No GUI, no window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Anti-detection options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # User agent to look like real browser
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Anti-detection script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("✅ Headless browser setup successful - no window will open")
        return driver

    except Exception as e:
        print(f"❌ Chrome setup error: {e}")
        print("💡 Make sure Chrome browser is installed")
        return None


def search_jobs(search_term="python developer", location="remote", max_jobs=10):
    """Search for jobs on LinkedIn without opening browser window"""

    print(f"🔍 Starting job search: '{search_term}' in '{location}'")

    driver = setup_browser()
    if not driver:
        print("❌ Failed to setup headless browser")
        return []

    jobs = []

    try:
        # Format search terms for URL
        search_encoded = search_term.replace(" ", "%20")
        location_encoded = location.replace(" ", "%20")

        # LinkedIn public jobs URL with filters for recent jobs
        url = f"https://www.linkedin.com/jobs/search/?keywords={search_encoded}&location={location_encoded}&f_TPR=r604800&sortBy=DD"

        print(f"📍 Accessing LinkedIn job search...")
        driver.get(url)

        # Wait for page load
        wait_time = random.uniform(3, 6)
        print(f"⏳ Loading page ({wait_time:.1f}s)...")
        time.sleep(wait_time)

        # Try multiple selectors to find job listings
        job_selectors = [
            "div[data-view-name='job-search-card']",
            ".job-search-card",
            ".base-card",
            ".base-search-card",
            "li.result-card",
            ".jobs-search__results-list li"
        ]

        job_cards = []
        for selector in job_selectors:
            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                    break
            except Exception:
                continue

        if not job_cards:
            print("❌ No job listings found. LinkedIn structure may have changed.")
            # Save page source for debugging
            with open("linkedin_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📄 Page source saved to linkedin_debug.html for analysis")
            return []

        print(f"📋 Processing up to {min(len(job_cards), max_jobs)} jobs...")

        for i, card in enumerate(job_cards[:max_jobs]):
            try:
                # Extract job title
                title = extract_text_with_selectors(card, [
                    "h3.base-search-card__title a",
                    ".base-search-card__title",
                    "h3 a span[title]",
                    "h3.job-search-card__title a",
                    ".job-title a",
                    "h3 a",
                    "h3"
                ])

                if not title or len(title) < 3:
                    continue

                # Extract company name
                company = extract_text_with_selectors(card, [
                    "h4.base-search-card__subtitle a",
                    ".base-search-card__subtitle",
                    "h4.job-search-card__subtitle a",
                    ".job-search-card__subtitle",
                    ".company-name a",
                    "h4 a",
                    "h4"
                ]) or "Company Not Specified"

                # Extract location
                location_text = extract_text_with_selectors(card, [
                    "span.job-search-card__location",
                    ".job-search-card__location",
                    ".job-result-card__location",
                    ".base-search-card__location",
                    ".job-search-card__metadata"
                ]) or "Location Not Specified"

                # Clean and validate data
                title = title.strip()
                company = company.strip()
                location_text = location_text.strip()

                if title and company:  # Both title and company required
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text
                    }
                    jobs.append(job)
                    print(f"✅ {len(jobs):2d}. {title[:40]}{'...' if len(title) > 40 else ''} @ {company}")

                # Small delay between processing jobs
                time.sleep(random.uniform(0.3, 1.0))

            except Exception as e:
                print(f"⚠️ Error processing job {i + 1}: {str(e)[:50]}...")
                continue

        if jobs:
            print(f"🎉 Successfully found {len(jobs)} jobs!")
        else:
            print("❌ No valid jobs could be extracted")

    except Exception as e:
        print(f"❌ Scraping error: {e}")

    finally:
        if driver:
            driver.quit()
            print("🔒 Browser closed")

    return jobs


def extract_text_with_selectors(element, selectors):
    """Try multiple CSS selectors to extract text"""
    for selector in selectors:
        try:
            found = element.find_element(By.CSS_SELECTOR, selector)
            # Try different text extraction methods
            text = found.get_attribute('title') or found.get_attribute('aria-label') or found.text
            if text and text.strip():
                return text.strip()
        except Exception:
            continue
    return None


if __name__ == "__main__":
    print("🤖 TESTING HEADLESS LINKEDIN SCRAPER")
    print("=" * 50)
    print("ℹ️ Browser will run in background - no window will open")

    # Test search
    jobs = search_jobs("Software Developer", "remote", max_jobs=5)

    if jobs:
        print(f"\n📊 SCRAPING RESULTS:")
        print(f"Total jobs found: {len(jobs)}")
        print("\n📋 Sample jobs:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print()
    else:
        print("\n❌ No jobs found. Check your internet connection.")

    print("✅ Test complete!")