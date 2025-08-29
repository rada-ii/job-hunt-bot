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
                    st.info(
                        "This might be due to Chrome/Chromium not being available on the server. Try the local version or check the logs.")

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

# Get all jobs for display
try:
    db = JobDatabase()
    all_jobs = db.get_all_jobs()
except Exception as e:
    st.error(f"Database error: {e}")
    all_jobs = []

# Metrics section
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f'''
    <div class="metric-card">
        <h2>{len(all_jobs) if all_jobs else 0}</h2>
        <p>Total Jobs</p>
    </div>
    ''', unsafe_allow_html=True)

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

# MAIN LAYOUT - Two columns for jobs and cover letter
job_col, cover_col = st.columns([1, 1])

with job_col:
    st.header("🔍 Found Jobs")

    if all_jobs:
        # Add search and filter options
        search_filter = st.text_input("🔍 Filter jobs", placeholder="Search by company or title...")
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

        # Job selection for cover letter
        if 'selected_job' not in st.session_state:
            st.session_state.selected_job = None

        for i, job in enumerate(filtered_jobs):
            # Job card with basic info
            st.markdown(f'''
            <div class="job-card">
                <div class="job-title">{job[1]}</div>
                <div class="job-company">🏢 {job[2]}</div>
                <div class="job-details">
                    📍 {job[3]} | 📅 Found: {job[4]}
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Accordion for detailed job information
            with st.expander(f"📖 Job Details - {job[1][:30]}..."):
                st.markdown(f"**📝 Position:** {job[1]}")
                st.markdown(f"**🏢 Company:** {job[2]}")
                st.markdown(f"**📍 Location:** {job[3]}")
                st.markdown(f"**📅 Date Found:** {job[4]}")

                # Select this job for cover letter generation
                if st.button(f"✍️ Select for Cover Letter", key=f"select_{job[0]}"):
                    st.session_state.selected_job = job
                    st.success(f"Selected: {job[1]} at {job[2]}")

            st.divider()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 10px; margin: 2rem 0;">
            <h3>🔍 No Jobs Found</h3>
            <p>Use the sidebar to search for jobs and get started!</p>
            <p>💡 Try searching for "Python developer", "Data scientist", or "Software engineer"</p>
        </div>
        """, unsafe_allow_html=True)

with cover_col:
    st.header("✍️ Cover Letter Generator")

    if st.session_state.selected_job:
        selected_job = st.session_state.selected_job
        st.info(f"📋 Selected Job: **{selected_job[1]}** at **{selected_job[2]}**")

        # Cover letter generation form
        st.markdown("### 📝 Personal Information")
        user_name = st.text_input("👤 Your Name", placeholder="John Doe")
        user_email = st.text_input("📧 Your Email", placeholder="john.doe@email.com")
        user_phone = st.text_input("📱 Your Phone", placeholder="+1 (555) 123-4567")

        st.markdown("### 💼 Experience")
        years_experience = st.selectbox("Years of Experience", ["0-1", "2-3", "4-5", "6-10", "10+"])
        key_skills = st.text_area("🔧 Key Skills", placeholder="Python, JavaScript, React, Machine Learning...")

        if st.button("🤖 Generate Cover Letter", type="primary", use_container_width=True):
            if user_name and user_email:
                try:
                    generator = CoverLetterGenerator()
                    with st.spinner("🤖 AI generating personalized cover letter..."):
                        # Create job context for better cover letter
                        job_context = {
                            'title': selected_job[1],
                            'company': selected_job[2],
                            'location': selected_job[3],
                            'user_name': user_name,
                            'user_email': user_email,
                            'user_phone': user_phone,
                            'years_experience': years_experience,
                            'key_skills': key_skills
                        }

                        cover_letter = generator.generate_cover_letter(
                            selected_job[1],
                            selected_job[2],
                            user_context=job_context
                        )

                        st.markdown("### 📄 Generated Cover Letter")
                        st.text_area("", cover_letter, height=400, key="generated_cover_letter")

                        # Download and copy options
                        col_download, col_clear = st.columns(2)
                        with col_download:
                            st.download_button(
                                "💾 Download Cover Letter",
                                cover_letter,
                                file_name=f"cover_letter_{selected_job[2].replace(' ', '_')}_{selected_job[1].replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                        with col_clear:
                            if st.button("🗑️ Clear Selection"):
                                st.session_state.selected_job = None
                                st.rerun()

                        st.success("✅ Cover letter generated successfully!")

                except Exception as e:
                    st.error(f"❌ Cover letter generation failed: {str(e)}")
                    st.info("Make sure your OpenAI API key is set in Streamlit secrets")
            else:
                st.warning("⚠️ Please fill in at least your name and email")
    else:
        st.info("👆 Select a job from the left panel to generate a cover letter")
        st.markdown("""
        ### How to use:
        1. **Search for jobs** using the sidebar
        2. **Select a job** by clicking "Select for Cover Letter" in job details
        3. **Fill in your information** here
        4. **Generate** your personalized cover letter
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>🤖 Job Hunt Bot | Built with ❤️ and Streamlit</p>
    <p style="font-size: 0.8rem;">For best scraping performance, run locally or ensure Chromium is installed on the server</p>
</div>
""", unsafe_allow_html=True)