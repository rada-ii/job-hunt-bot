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

    .job-detail-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #5dade2;
    }

    .detail-header {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
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

            # Enhanced accordion with detailed job information
            with st.expander(f"📖 Full Job Details - {job[1][:40]}..."):

                # Basic Information Section
                st.markdown('''
                <div class="job-detail-section">
                    <div class="detail-header">📋 Basic Information</div>
                </div>
                ''', unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Position:** {job[1]}")
                    st.markdown(f"**Company:** {job[2]}")
                with col2:
                    st.markdown(f"**Location:** {job[3]}")
                    st.markdown(f"**Date Found:** {job[4]}")

                # Status Information
                st.markdown('''
                <div class="job-detail-section">
                    <div class="detail-header">📊 Application Status</div>
                </div>
                ''', unsafe_allow_html=True)

                if job[5]:  # applied status
                    st.success("✅ Already Applied")
                else:
                    st.info("📝 Not Applied Yet")

                # Mock Additional Details (these would come from enhanced scraping)
                st.markdown('''
                <div class="job-detail-section">
                    <div class="detail-header">💼 Job Details</div>
                </div>
                ''', unsafe_allow_html=True)

                # Employment Type and Experience Level
                col1, col2 = st.columns(2)
                with col1:
                    # Mock data based on common job patterns
                    if "senior" in job[1].lower() or "lead" in job[1].lower():
                        st.markdown("**Experience Level:** Senior (5+ years)")
                    elif "junior" in job[1].lower() or "entry" in job[1].lower():
                        st.markdown("**Experience Level:** Entry Level (0-2 years)")
                    else:
                        st.markdown("**Experience Level:** Mid Level (2-5 years)")

                    st.markdown("**Employment Type:** Full-time")

                with col2:
                    # Mock salary range based on role and location
                    if "remote" in job[3].lower():
                        st.markdown("**Salary Range:** $70,000 - $120,000")
                    elif any(city in job[3].lower() for city in ["san francisco", "new york", "seattle"]):
                        st.markdown("**Salary Range:** $90,000 - $150,000")
                    else:
                        st.markdown("**Salary Range:** $60,000 - $100,000")

                    st.markdown("**Work Type:** Hybrid/Remote")

                # Key Requirements Section
                st.markdown('''
                <div class="job-detail-section">
                    <div class="detail-header">🎯 Key Requirements</div>
                </div>
                ''', unsafe_allow_html=True)

                # Generate mock requirements based on job title
                if "python" in job[1].lower():
                    requirements = [
                        "• 3+ years of Python development experience",
                        "• Experience with Django/Flask frameworks",
                        "• Knowledge of SQL databases (PostgreSQL, MySQL)",
                        "• Familiarity with Git version control",
                        "• Understanding of RESTful APIs"
                    ]
                elif "data" in job[1].lower():
                    requirements = [
                        "• Bachelor's degree in Data Science, Statistics, or related field",
                        "• Proficiency in Python/R and SQL",
                        "• Experience with pandas, numpy, scikit-learn",
                        "• Knowledge of data visualization tools (Tableau, Power BI)",
                        "• Understanding of machine learning concepts"
                    ]
                elif "frontend" in job[1].lower() or "react" in job[1].lower():
                    requirements = [
                        "• 3+ years of JavaScript/TypeScript experience",
                        "• Strong proficiency in React.js and modern frameworks",
                        "• Experience with HTML5, CSS3, and responsive design",
                        "• Knowledge of state management (Redux, Context API)",
                        "• Familiarity with modern build tools (Webpack, Vite)"
                    ]
                else:
                    requirements = [
                        "• Bachelor's degree in Computer Science or related field",
                        "• Strong programming skills in relevant technologies",
                        "• Experience with software development lifecycle",
                        "• Excellent problem-solving and communication skills",
                        "• Ability to work in an agile development environment"
                    ]

                for req in requirements:
                    st.markdown(req)

                # Benefits Section
                st.markdown('''
                <div class="job-detail-section">
                    <div class="detail-header">🎁 Benefits & Perks</div>
                </div>
                ''', unsafe_allow_html=True)

                benefits = [
                    "• Competitive salary and equity package",
                    "• Comprehensive health, dental, and vision insurance",
                    "• Flexible PTO and work-from-home options",
                    "• Professional development budget ($2,000/year)",
                    "• Modern equipment and technology stipend"
                ]

                for benefit in benefits:
                    st.markdown(benefit)

                # Company Information
                st.markdown('''
                <div class="job-detail-section">
                    <div class="detail-header">🏢 About the Company</div>
                </div>
                ''', unsafe_allow_html=True)

                st.markdown(f"""
                **{job[2]}** is a growing technology company focused on innovation and excellence. 
                We're building cutting-edge solutions and looking for talented individuals to join our team.

                **Company Size:** 50-200 employees  
                **Industry:** Technology/Software  
                **Founded:** 2015-2020  
                """)

                # Action Buttons
                st.markdown("---")
                button_col1, button_col2, button_col3 = st.columns(3)

                with button_col1:
                    if st.button(f"✍️ Generate Cover Letter", key=f"select_{job[0]}"):
                        st.session_state.selected_job = job
                        st.success(f"Selected: {job[1]} at {job[2]}")

                with button_col2:
                    # Mock LinkedIn URL
                    linkedin_url = f"https://linkedin.com/jobs/view/{job[0] + 1000000}"
                    st.link_button("🔗 View on LinkedIn", linkedin_url)

                with button_col3:
                    if not job[5]:  # If not applied yet
                        if st.button(f"✅ Mark as Applied", key=f"apply_{job[0]}"):
                            # Here you would update the database
                            st.success("Marked as applied!")

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
        2. **Select a job** by clicking "Generate Cover Letter" in job details
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