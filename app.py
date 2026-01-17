import streamlit as st
import asyncio
import sys
from scraper import JobScraper
from models import JobData
import ui  # Imported from our new ui.py

# Windows-specific fix for Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Page Config
st.set_page_config(
    page_title="JobLens",
    page_icon="💼",
    layout="wide"
)

# Load Styles
ui.load_css()
ui.render_header()

# Input Section (Compact)
col_input, col_btn = st.columns([4, 1])
with col_input:
    url = st.text_input("Job URL", placeholder="Paste job link here...", label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button("Analyze", use_container_width=True)

if analyze_btn and url:
    with st.spinner("Analyzing..."):
        try:
            scraper = JobScraper()
            job_data = scraper.scrape_job(url)
            
            st.markdown("---")
            
            # --- Split Layout ---
            # Left: Metrics (Cards)
            # Right: Description (Main Content)
            left_col, right_col = st.columns([1, 2], gap="large")
            
            with left_col:
                st.subheader("Key Details")
                ui.render_metric_card("Position", job_data.title)
                ui.render_metric_card("Company", job_data.company)
                
                # Posted Date with Sub-value (Time)
                rel_date = ui.format_date_relative(job_data.date_posted)
                abs_date = ui.format_date_absolute(job_data.date_posted)
                ui.render_metric_card("Posted", rel_date, sub_value=abs_date)
                
                # Logic for Applicants
                # Note: We can only show what the page explicitly states.
                app_count = job_data.applicants
                if app_count == "Not Public/Visible":
                    app_count_display = "N/A (Hidden by Employer)"
                else:
                    app_count_display = app_count
                    
                ui.render_metric_card("Applicants", app_count_display)
                
                with st.expander("json source"):
                     # Fixed: using model_dump() instead of dict()
                    st.json(job_data.model_dump())

            with right_col:
                st.subheader("Job Description")
                with st.container(height=600): # Scrollable container
                    st.markdown(job_data.description_markdown)

        except Exception as e:
            st.error(f"Error: {e}")
elif analyze_btn:
    st.warning("Please enter a URL.")
