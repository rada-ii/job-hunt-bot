# Job Hunt Bot - AI Automation Assistant

Professional job hunting automation with AI-powered cover letter generation and ethical compliance design.

## 🌐 Live Demo

**[Try Job Hunt Bot](https://job-hunt-bot.up.railway.app/)**

## ✨ Features

* **🔍 Automated Job Discovery** - Scrapes LinkedIn for relevant positions based on search criteria
* **🤖 AI-Powered Cover Letters** - Generates personalized applications using OpenAI GPT-3.5
* **📊 Application Tracking** - SQLite database stores jobs with duplicate prevention
* **💻 Web Dashboard** - Streamlit interface for job management and cover letter generation
* **⚖️ Ethical Design** - Human-in-the-loop approach respects platform terms of service

## 🛠️ Technology Stack

**Backend:**
* Python 3.11+ with Selenium WebDriver for web automation
* SQLite for local data storage
* OpenAI API for intelligent text generation

**Frontend:**
* Streamlit for web interface and deployment

**Automation:**
* BeautifulSoup for HTML parsing
* Webdriver Manager for browser setup
* Anti-detection measures with random delays

## 📋 Installation & Setup

1. **Clone repository:**
```bash
git clone https://github.com/rada-ii/job-hunt-bot.git
cd job-hunt-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:** Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Run the application:**
```bash
streamlit run dashboard/streamlit_app.py
```

## 🎯 Usage

1. **Search Jobs:** Enter search terms in sidebar (e.g., "Python developer", "remote")
2. **Discover Positions:** Click "Search Jobs" to scrape LinkedIn for relevant openings
3. **Browse Results:** View found jobs in main interface with company and location details
4. **Generate Cover Letters:** Click "Generate Cover Letter" for AI-powered personalized applications
5. **Apply Manually:** Copy generated cover letters for professional application submission

## 📁 Project Structure

```
job-hunt-bot/
├── main.py                    # Command line entry point
├── dashboard/streamlit_app.py # Web interface
├── scrapers/linkedin_scraper.py # LinkedIn job scraping logic
├── ai/cover_letter_gen.py     # OpenAI cover letter generation
├── database/                  # SQLite storage and models
├── config/settings.json       # User preferences and search parameters
└── requirements.txt           # Python dependencies
```

## 💡 Design Philosophy

**Ethical Automation:** This tool automates time-consuming research and preparation tasks while maintaining authentic human communication. Manual application submission ensures compliance with LinkedIn Terms of Service and promotes genuine professional networking.

**Human-in-the-Loop:** Automated job discovery and cover letter generation combined with manual job selection and application submission for sustainable, authentic job searching.

## 🔧 Technical Features

* **Anti-Detection:** Random delays, stealth browser configuration, multiple CSS selector fallbacks
* **Error Handling:** Graceful failure recovery, duplicate prevention, API error management
* **Data Management:** Local SQLite storage with automatic database initialization
* **Email Validation:** Built-in validation for professional contact information
* **Export Functionality:** Download cover letters as text files

## 🚨 Troubleshooting

**ChromeDriver Issues:**
```bash
pip install --upgrade webdriver-manager
```

**OpenAI API Errors:**
* Verify API key in `.env` file
* Check API usage limits and account status

**Streamlit Issues:**
* Ensure all dependencies are installed
* Check Python version compatibility (3.11+)

## 📄 License

MIT License - Educational and portfolio use.

---

**Built with ❤️ by Rada Ivanković | Python, OpenAI, and ethical automation practices.**
