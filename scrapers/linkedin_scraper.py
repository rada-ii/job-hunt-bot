from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import random
import os
import platform


def setup_browser():
    """Setup Chrome browser - works both locally and on Streamlit Cloud"""
    chrome_options = Options()

    # Essential headless options
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Anti-detection options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # User agent
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Additional cloud-specific options
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")  # Remove if JS is needed
    chrome_options.add_argument("--disable-plugins-discovery")

    try:
        # Try different Chrome/Chromium paths based on environment
        if platform.system() == "Linux":
            # Streamlit Cloud / Linux environment
            chrome_paths = [
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/usr/bin/google-chrome",
                "/usr/bin/chrome"
            ]

            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    chrome_options.binary_location = chrome_path
                    print(f"Using Chrome at: {chrome_path}")
                    break

        # Try to create driver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Fallback to system Chrome
            driver = webdriver.Chrome(options=chrome_options)

        # Anti-detection script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("Browser setup successful - headless mode")
        return driver

    except Exception as e:
        print(f"Chrome setup error: {e}")
        print("Make sure Chrome/Chromium is installed")
        return None


def search_jobs(search_term="python developer", location="remote", max_jobs=10):
    """Search for jobs on LinkedIn - cloud compatible"""

    print(f"Starting job search: '{search_term}' in '{location}'")

    driver = setup_browser()
    if not driver:
        print("Failed to setup browser")
        return []

    jobs = []

    try:
        # Format search terms for URL
        search_encoded = search_term.replace(" ", "%20")
        location_encoded = location.replace(" ", "%20")

        # LinkedIn public jobs URL
        url = f"https://www.linkedin.com/jobs/search/?keywords={search_encoded}&location={location_encoded}&f_TPR=r604800&sortBy=DD"

        print(f"Accessing: {url}")
        driver.get(url)

        # Wait for page load
        wait_time = random.uniform(4, 7)
        print(f"Loading page ({wait_time:.1f}s)...")
        time.sleep(wait_time)

        # Try multiple selectors to find job listings
        job_selectors = [
            "div[data-view-name='job-search-card']",
            ".job-search-card",
            ".base-card",
            ".base-search-card",
            "li.result-card",
            ".jobs-search__results-list li",
            ".job-card-container",
            "[data-entity-urn*='job']"
        ]

        job_cards = []
        for selector in job_selectors:
            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    print(f"Found {len(job_cards)} jobs using: {selector}")
                    break
            except Exception:
                continue

        if not job_cards:
            print("No job listings found")
            # Save page source for debugging
            try:
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("Page source saved to debug_page.html")
            except:
                pass
            return []

        print(f"Processing up to {min(len(job_cards), max_jobs)} jobs...")

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
                    "h3",
                    ".job-card__title a",
                    "[data-control-name='job_search_job_title']"
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
                    "h4",
                    ".job-card__company-name a"
                ]) or "Company Not Listed"

                # Extract location
                location_text = extract_text_with_selectors(card, [
                    "span.job-search-card__location",
                    ".job-search-card__location",
                    ".job-result-card__location",
                    ".base-search-card__location",
                    ".job-search-card__metadata",
                    ".job-card__location"
                ]) or "Location Not Listed"

                # Clean and validate data
                title = title.strip()
                company = company.strip()
                location_text = location_text.strip()

                # Remove unwanted text
                for unwanted in ["new", "promoted", "easy apply", "actively recruiting"]:
                    title = title.replace(unwanted, "").strip()
                    company = company.replace(unwanted, "").strip()

                if title and company and len(title) > 2:
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text
                    }
                    jobs.append(job)
                    print(f"{len(jobs):2d}. {title[:50]}{'...' if len(title) > 50 else ''} @ {company}")

                # Delay between processing
                time.sleep(random.uniform(0.5, 2.0))

            except Exception as e:
                print(f"Error processing job {i + 1}: {str(e)[:50]}...")
                continue

        if jobs:
            print(f"Successfully found {len(jobs)} jobs!")
        else:
            print("No valid jobs could be extracted")

    except Exception as e:
        print(f"Scraping error: {e}")

    finally:
        if driver:
            driver.quit()
            print("Browser closed")

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
    print("Testing LinkedIn Job Scraper (Cloud Compatible)")
    print("=" * 60)

    # Test search
    jobs = search_jobs("Software Developer", "remote", max_jobs=5)

    if jobs:
        print(f"\nSCRAPING RESULTS:")
        print(f"Total jobs found: {len(jobs)}")
        print("\nSample jobs:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print()
    else:
        print("\nNo jobs found. Check internet connection or LinkedIn structure changes.")

    print("Test complete!")