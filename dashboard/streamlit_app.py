import streamlit as st
import sys
import os
import time

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
        position: relative;
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
        margin-bottom: 1rem;
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

    /* Remove custom container - use normal browser scroll */
    .jobs-list {
        padding: 0;
    }

    /* Footer fixed to bottom */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        text-align: center;
        padding: 15px;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }

    /* Add bottom padding to main content so footer doesn't overlap */
    .main-content {
        padding-bottom: 80px;
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
                        # Quick success message - 1.5s
                        success_placeholder = st.success(f"✅ Found {len(jobs)} jobs, saved {saved} new ones!")
                        time.sleep(1.5)
                        success_placeholder.empty()
                        st.rerun()  # Refresh to show new jobs
                    else:
                        error_placeholder = st.error("❌ No jobs found - LinkedIn may be blocking or structure changed")
                        time.sleep(1.5)
                        error_placeholder.empty()
                except Exception as e:
                    error_placeholder = st.error(f"❌ Search failed: {str(e)}")
                    time.sleep(2)
                    error_placeholder.empty()

    with search_col2:
        if st.button("🗑️ Clear DB", use_container_width=True):
            try:
                db = JobDatabase()
                # Properly clear the database
                db.clear_all_jobs()  # Use the existing method
                success_placeholder = st.success("✅ Database cleared!")
                time.sleep(1.5)  # Quick message - 1.5 seconds only
                success_placeholder.empty()
                st.rerun()  # Refresh to show empty state
            except Exception as e:
                error_placeholder = st.error(f"❌ Clear failed: {str(e)}")
                time.sleep(1.5)
                error_placeholder.empty()

# Debug info (remove in production)
with st.sidebar:
    st.markdown("---")
    if st.checkbox("🐛 Debug Info"):
        try:
            db = JobDatabase()
            st.write(f"Database path: {db.db_path}")
            st.write(f"Platform: {os.name}")
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

# Initialize session state for cover letter functionality
if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None
if 'generated_letter' not in st.session_state:
    st.session_state.generated_letter = None
if 'ai_polish_enabled' not in st.session_state:
    # Default to True if API key is available
    st.session_state.ai_polish_enabled = bool(os.getenv('OPENAI_API_KEY'))

# Main content wrapper
st.markdown('<div class="main-content">', unsafe_allow_html=True)

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

        # Jobs list - NO custom container, use natural browser scroll
        for i, job in enumerate(filtered_jobs):
            # Job info without custom HTML div
            st.markdown(f"### {job[1]}")
            st.markdown(f"🏢 **{job[2]}**")
            st.markdown(f"📍 {job[3]} | 📅 Found: {job[4]} {f'| ✅ Applied' if job[5] else ''}")

            # Generate Cover Letter button
            if st.button(f"✍️ Generate Cover Letter", key=f"select_{job[0]}", use_container_width=True):
                # Set selected job and reset generated letter to trigger new generation
                st.session_state.selected_job = job
                st.session_state.generated_letter = None
                
                # Generate cover letter automatically
                try:
                    generator = CoverLetterGenerator()
                    with st.spinner("🤖 Generating cover letter..."):
                        cover_letter = generator.generate_cover_letter(
                            job[1],  # job_title
                            job[2],  # company_name
                            job[3],  # location
                            use_ai=st.session_state.ai_polish_enabled
                        )
                        st.session_state.generated_letter = cover_letter
                        
                    success_placeholder = st.success(f"✅ Generated cover letter for {job[1][:30]}...")
                    time.sleep(1.5)
                    success_placeholder.empty()
                    st.rerun()
                except Exception as e:
                    error_placeholder = st.error(f"❌ Generation failed: {str(e)}")
                    time.sleep(2)
                    error_placeholder.empty()

            st.divider()  # Clean separator between jobs

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
        
        # Display job information
        st.markdown("### 📋 Selected Job")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.write(f"**Title:** {selected_job[1]}")
            st.write(f"**Company:** {selected_job[2]}")
        with col_info2:
            st.write(f"**Location:** {selected_job[3]}")
            st.write(f"**Date Found:** {selected_job[4]}")
        
        st.divider()
        
        # Cover Letter Controls
        if st.session_state.generated_letter:
            st.markdown("### 📄 Generated Cover Letter")
            
            # Controls row
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                # AI Polish toggle (only show if API key available)
                if os.getenv('OPENAI_API_KEY'):
                    ai_toggle = st.checkbox(
                        "🤖 AI Polish", 
                        value=st.session_state.ai_polish_enabled,
                        help="Use AI to enhance the cover letter"
                    )
                    if ai_toggle != st.session_state.ai_polish_enabled:
                        st.session_state.ai_polish_enabled = ai_toggle
                else:
                    st.info("💡 AI polish unavailable (no API key)")
            
            with control_col2:
                if st.button("🔄 Regenerate", use_container_width=True, help="Generate a new version"):
                    try:
                        generator = CoverLetterGenerator()
                        with st.spinner("🤖 Regenerating..."):
                            cover_letter = generator.generate_cover_letter(
                                selected_job[1],  # job_title
                                selected_job[2],  # company_name
                                selected_job[3],  # location
                                use_ai=st.session_state.ai_polish_enabled
                            )
                            st.session_state.generated_letter = cover_letter
                            st.success("✅ Regenerated!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Regeneration failed: {str(e)}")
            
            with control_col3:
                if st.button("📝 Use Basic Version", use_container_width=True, help="Switch to deterministic version"):
                    try:
                        generator = CoverLetterGenerator()
                        with st.spinner("📝 Generating basic version..."):
                            cover_letter = generator.generate_cover_letter(
                                selected_job[1],  # job_title
                                selected_job[2],  # company_name
                                selected_job[3],  # location
                                use_ai=False
                            )
                            st.session_state.generated_letter = cover_letter
                            st.session_state.ai_polish_enabled = False
                            st.success("✅ Switched to basic version!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to generate basic version: {str(e)}")
            
            # Display the generated letter (read-only)
            st.text_area(
                "",
                st.session_state.generated_letter,
                height=400,
                disabled=True,  # Read-only
                key="display_letter",
                help="This is your generated cover letter"
            )
            
            # Action buttons row
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                st.download_button(
                    "💾 Download Cover Letter",
                    st.session_state.generated_letter,
                    file_name=f"cover_letter_{selected_job[2].replace(' ', '_')}_{selected_job[1].replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with action_col2:
                if st.button("🗑️ Clear & Change Job", use_container_width=True):
                    st.session_state.selected_job = None
                    st.session_state.generated_letter = None
                    st.success("✅ Cleared! Select a new job.")
                    time.sleep(1.5)
                    st.rerun()
        
        else:
            # No letter generated yet - show generating message
            with st.spinner("🤖 Generating your cover letter automatically..."):
                try:
                    generator = CoverLetterGenerator()
                    cover_letter = generator.generate_cover_letter(
                        selected_job[1],  # job_title
                        selected_job[2],  # company_name
                        selected_job[3],  # location
                        use_ai=st.session_state.ai_polish_enabled
                    )
                    st.session_state.generated_letter = cover_letter
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
                    st.info("💡 Please try again or contact support if the issue persists.")
    
    else:
        st.info("👆 Select a job from the left panel to automatically generate a cover letter")
        st.markdown("""
        ### How to use:
        1. **Search for jobs** using the sidebar
        2. **Click "✍️ Generate Cover Letter"** next to any job
        3. **Cover letter is generated automatically** - no personal input needed!
        4. **Download or regenerate** as needed
        """)

# Close main content wrapper
st.markdown('</div>', unsafe_allow_html=True)

# Fixed footer at bottom of page
st.markdown("""
<div class="footer">
    <p>🤖 <strong>Job Hunt Bot</strong> | Built with ❤️ by <strong>Rada Ivanković</strong> | Powered by Streamlit & AI</p>
</div>
""", unsafe_allow_html=True)