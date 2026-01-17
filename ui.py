import streamlit as st
from datetime import datetime

# --- Premium CSS ---
CUSTOM_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background-color: #f8f9fc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Compact Header */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid #e2e8f0;
    }
    .header-title {
        font-size: 1.8em;
        font-weight: 800;
        background: linear-gradient(to right, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-right: 15px;
    }
    .header-subtitle {
        color: #64748b;
        font-size: 1em;
        font-weight: 400;
        margin-top: 5px;
    }

    /* Metric Card Styling */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        margin-bottom: 15px;
        text-align: left;
    }
    .metric-label {
        font-size: 0.75em;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.1em;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
        word-wrap: break-word;
    }
    .metric-sub-value {
        font-size: 0.8em;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white;
        border: none;
        font-weight: 600;
    }

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column;
            align-items: flex-start;
            padding-bottom: 10px;
        }
        .header-title {
            font-size: 1.5em; /* Smaller title */
            margin-bottom: 5px;
        }
        .header-subtitle {
            font-size: 0.9em;
        }
        .metric-card {
            padding: 15px; /* Compact padding */
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 1em;
        }
    }
</style>
"""

def load_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_header():
    st.markdown("""
        <div class="header-container">
            <div class="header-title">JobLens</div>
            <div class="header-subtitle">Intelligent insights for your next career move</div>
        </div>
    """, unsafe_allow_html=True)

def format_date_relative(date_str):
    """Parses ISO date string and returns a human-readable relative time."""
    if not date_str or date_str == "N/A":
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days == 0: return "Today"
        if diff.days == 1: return "Yesterday"
        if diff.days < 30: return f"{diff.days} days ago"
        months = diff.days // 30
        if months < 12: return f"{months} month{'s' if months > 1 else ''} ago"
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def format_date_absolute(date_str):
    """Returns exact date and time, e.g., 'Oct 29, 2025 • 07:01 AM'"""
    if not date_str or date_str == "N/A":
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y • %I:%M %p")
    except:
        return ""

def render_metric_card(label, value, sub_value=None):
    sub_html = f'<div class="metric-sub-value">{sub_value}</div>' if sub_value else ''
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)
