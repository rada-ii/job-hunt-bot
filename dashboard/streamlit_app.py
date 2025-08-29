import streamlit as st
import sys
import os

# Add project root to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.linkedin_scraper import search_jobs
from database.db_manager import JobDatabase
from ai.cover_letter_gen import CoverLetterGenerator

# Page configuration
st.set_page_config(
    page_title="Job Hunt Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #5dade2 0%, #85c1e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }

    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #5dade2;
    }

    .job-title {
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .job-company {
        color: #5dade2;
        font-size: 1.1rem;
        font-weight: 600;
    }

    .job-details {
        color: #7f8c8d;
        font-size: 0.9rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #5dade2 0%, #85c1e9 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }

    .sidebar-header {
        background: linear-gradient(135deg, #5dade2 0%, #85c1e9 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🤖 Job Hunt Bot Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h2>Search Controls</h2></div>', unsafe_allow_html=True)

    st.markdown("### 🎯 Job Search")
    search_term = st.text_input("🔍 Search Term", value="Python developer", help="Enter job title or keywords")
    location = st.text_input("📍 Location", value="remote", help="City, state, or 'remote'")

    st.markdown("### ⚙️ Filters")
    job_type = st.selectbox("💼 Job Type", ["All", "Full-time", "Part-time", "Contract", "Internship"])
    experience_level = st.selectbox("📊 Experience Level", ["All", "Entry", "Mid", "Senior", "Executive"])

    st.markdown("---")

    search_col1, search_col2 = st.columns(2)
    with search_col1:
        if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
            with st.spinner("🔄 Scraping LinkedIn..."):
                try:
                    jobs = search_jobs(search_term, location)
                    if jobs:
                        db = JobDatabase()
                        saved = db.save_jobs(jobs)
                        st.success(f"✅ Found {len(jobs)} jobs, saved {saved} new ones!")
                        st.rerun()  # Refresh to show new jobs
                    else:
                        st.error("❌ No jobs found - LinkedIn may be blocking or structure changed")
                except Exception as e:
                    st.error(f"❌ Search failed: {str(e)}")
                    st.info("This might be due to Chrome/Chromium not being available on the server. Try the local version or check the logs.")

    with search_col2:
        if st.button("🗑️ Clear DB", use_container_width=True):
            try:
                db = JobDatabase()
                db.clear_all_jobs()
                st.success("✅ Database cleared!")
                st.rerun()  # Refresh to show empty state
            except Exception as e:
                st.error(f"❌ Clear failed: {str(e)}")

# Debug info (remove in production)
with st.sidebar:
    st.markdown("---")
    if st.checkbox("🐛 Debug Info"):
        db = JobDatabase()
        st.write(f"Database path: {db.db_path}")
        st.write(f"Platform: {os.name}")
        try:
            jobs = db.get_all_jobs()
            st.write(f"Jobs in DB: {len(jobs)}")
        except Exception as e:
            st.write(f"DB Error: {e}")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    try:
        db = JobDatabase()
        all_jobs = db.get_all_jobs()
        st.markdown(f'''
        <div class="metric-card">
            <h2>{len(all_jobs) if all_jobs else 0}</h2>
            <p>Total Jobs</p>
        </div>
        ''', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Database error: {e}")
        all_jobs = []

with col2:
    if all_jobs:
        companies = list(set([job[2] for job in all_jobs]))
        st.markdown(f'''
        <div class="metric-card">
            <h2>{len(companies)}</h2>
            <p>Companies</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="metric-card">
            <h2>0</h2>
            <p>Companies</p>
        </div>
        ''', unsafe_allow_html=True)

st.markdown("---")

# Jobs display section
st.markdown("## 📋 Available Positions")

if all_jobs:
    # Add search and filter options
    col1, col2 = st.columns([3, 1])
    with col1:
        search_filter = st.text_input("🔍 Filter jobs", placeholder="Search by company or title...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Most Recent", "Company A-Z", "Title A-Z"])

    # Filter jobs based on search
    filtered_jobs = all_jobs
    if search_filter:
        filtered_jobs = [job for job in all_jobs if
                         search_filter.lower() in job[1].lower() or
                         search_filter.lower() in job[2].lower()]

    # Sort jobs
    if sort_by == "Company A-Z":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x[2])
    elif sort_by == "Title A-Z":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x[1])

    for i, job in enumerate(filtered_jobs):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f'''
            <div class="job-card">
                <div class="job-title">{job[1]}</div>
                <div class="job-company">🏢 {job[2]}</div>
                <div class="job-details">
                    📍 {job[3]} | 📅 Found: {job[4]}
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 Generate Cover Letter", key=f"btn_{job[0]}", type="secondary"):
                try:
                    generator = CoverLetterGenerator()
                    with st.spinner("🤖 AI generating cover letter template..."):
                        cover_letter = generator.generate_cover_letter(job[1], job[2])

                        # Show cover letter in a modal-like expander
                        with st.expander("📄 Generated Cover Letter Template", expanded=True):
                            st.markdown("### Professional Cover Letter Template")
                            st.text_area("", cover_letter, height=400, key=f"cover_{job[0]}")

                            col_download, col_copy = st.columns(2)
                            with col_download:
                                st.download_button(
                                    "💾 Download Template",
                                    cover_letter,
                                    file_name=f"cover_letter_template_{job[2].replace(' ', '_')}_{job[1].replace(' ', '_')}.txt",
                                    mime="text/plain",
                                    key=f"download_{job[0]}"
                                )
                            with col_copy:
                                st.info("💡 Copy the template above and customize with your details!")
                except Exception as e:
                    st.error(f"❌ Cover letter generation failed: {str(e)}")
                    st.info("Make sure your OpenAI API key is set in Streamlit secrets")

else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 10px; margin: 2rem 0;">
        <h3>🔍 No Jobs Found</h3>
        <p>Use the sidebar to search for jobs and get started!</p>
        <p>💡 Try searching for "Python developer", "Data scientist", or "Software engineer"</p>
        <p style="font-size: 0.9rem; color: #666;">Note: LinkedIn scraping may not work on cloud environments without proper Chrome/Chromium setup</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>🤖 Job Hunt Bot | Built with ❤️ and Streamlit</p>
    <p style="font-size: 0.8rem;">For best scraping performance, run locally or ensure Chromium is installed on the server</p>
</div>
""", unsafe_allow_html=True)