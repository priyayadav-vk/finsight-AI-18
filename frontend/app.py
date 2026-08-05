"""
FinSight AI - Main Streamlit Application
Intelligent Stock Market Prediction & Investment Assistant
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import *
from backend.utils.data_fetcher import DataFetcher

# ==================== PAGE CONFIG ====================
st.set_page_config(**STREAMLIT_CONFIG)

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: "Segoe UI", Arial, sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Headers */
    h1 {
        color: #0f172a;
        text-align: left;
        font-size: 2rem;
        margin-bottom: 0.35rem;
        font-weight: 700;
    }

    h2 {
        color: #1d4ed8;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 0.35rem;
        margin-top: 1.2rem;
    }

    h3 {
        color: #0f172a;
    }

    /* Text styling */
    body, p, div, span {
        color: #334155;
    }

    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        border-left: 4px solid #1d4ed8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }

    /* Button styling */
    .stButton > button {
        background-color: #1d4ed8;
        color: white;
        border: none;
        border-radius: 0.4rem;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #2563eb;
    }

    /* Success/danger badges */
    .success-badge {
        color: #059669;
        font-weight: bold;
    }

    .danger-badge {
        color: #dc2626;
        font-weight: bold;
    }

    .warning-badge {
        color: #d97706;
        font-weight: bold;
    }

    /* Make tables/cards easier to read */
    .stDataFrame, .stDataFrame > div {
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    
    if 'selected_exchange' not in st.session_state:
        st.session_state.selected_exchange = 'NSE'
    
    if 'current_ticker' not in st.session_state:
        st.session_state.current_ticker = None
    
    if 'live_data' not in st.session_state:
        st.session_state.live_data = None
    
    if 'prediction_data' not in st.session_state:
        st.session_state.prediction_data = None
    
    if 'threshold' not in st.session_state:
        st.session_state.threshold = DEFAULT_THRESHOLD
    
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    if 'yahoo_status_available' not in st.session_state:
        st.session_state.yahoo_status_available = None
    
    if 'yahoo_status_message' not in st.session_state:
        st.session_state.yahoo_status_message = ''
    
    if 'yahoo_status_checked_at' not in st.session_state:
        st.session_state.yahoo_status_checked_at = ''


# ==================== HELPER FUNCTIONS ====================

def get_ticker_for_exchange(company_info, exchange):
    """
    Get ticker for selected exchange.
    
    Parameters:
    -----------
    company_info : dict
        Company info with NSE/BSE tickers
    exchange : str
        'NSE' or 'BSE'
    
    Returns:
    --------
    str : Ticker symbol
    """
    if exchange == 'NSE':
        return company_info.get('NSE', company_info.get('BSE'))
    else:
        return company_info.get('BSE', company_info.get('NSE'))


def create_gradient_header(title, subtitle=""):
    """
    Create a beautiful gradient header.
    
    Parameters:
    -----------
    title : str
        Main title
    subtitle : str
        Subtitle (optional)
    """
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1f77b4 0%, #ff7f0e 100%);
                padding: 2rem;
                border-radius: 0.5rem;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <h1 style="color: white; margin-bottom: 0;">📈 {title}</h1>
                {'<p style="color: #f0f0f0; margin: 0;">' + subtitle + '</p>' if subtitle else ''}
            </div>
        """, unsafe_allow_html=True)


def display_metric_card(label, value, unit="", icon="", color="primary"):
    """
    Display a metric card.
    
    Parameters:
    -----------
    label : str
        Metric label
    value : float/str
        Metric value
    unit : str
        Unit of measurement
    icon : str
        Emoji icon
    color : str
        Color theme
    """
    colors = {
        'primary': '#1f77b4',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff9800'
    }
    
    card_color = colors.get(color, colors['primary'])
    
    st.markdown(f"""
        <div style="
            background-color: #161b22;
            border-left: 4px solid {card_color};
            padding: 1rem;
            border-radius: 0.25rem;
            margin: 0.5rem 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #8b949e; font-size: 0.9rem;">{label}</span>
                <span style="color: {card_color}; font-size: 1.5rem; font-weight: bold;">
                    {icon} {value} {unit}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def update_yahoo_validation_status(fetcher, force_refresh=False):
    """Update Streamlit session state with Yahoo Finance validation status."""
    if force_refresh or st.session_state.yahoo_status_available is None:
        status = fetcher.check_yahoo_status()
        st.session_state.yahoo_status_available = status['available']
        st.session_state.yahoo_status_message = status['message']
        st.session_state.yahoo_status_checked_at = status['last_checked']
    return {
        'available': st.session_state.yahoo_status_available,
        'message': st.session_state.yahoo_status_message,
        'last_checked': st.session_state.yahoo_status_checked_at
    }


# ==================== MAIN APP ====================

def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0.75rem; margin-bottom: 1rem;">
                <div style="font-size: 1.6rem; color: #1d4ed8; font-weight: 700; margin: 0;">📘 FinSight AI</div>
                <p style="color: #64748b; font-size: 0.88rem; margin-top: 0.45rem; margin-bottom: 0;">
                    Student Stock Predictor
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Home", "📊 Dashboard", "🔮 Prediction", "📈 Charts", "🤖 AI Insights", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")

        fetcher = DataFetcher()
        status = update_yahoo_validation_status(fetcher)
        if st.button("🔄 Check Yahoo status"):
            status = update_yahoo_validation_status(fetcher, force_refresh=True)

        st.markdown("### Yahoo Validation")
        if status['available'] is True:
            st.success("Yahoo Finance validation is available.")
            st.caption(status['message'])
        elif status['available'] is False:
            st.error("Yahoo Finance validation is unavailable.")
            st.caption(status['message'])
        else:
            st.info("Yahoo Finance validation has not been checked yet.")

        if status['last_checked']:
            st.caption(f"Last checked: {status['last_checked']}")
        
        st.markdown("---")
        
        # Project Info
        st.markdown("### Project Info")
        st.info(f"""
        **College:** {COLLEGE}
        
        **Course:** {COURSE}
        
        **Companies:** {len(INDIAN_COMPANIES)}
        
        **Model:** {MODEL_CONFIG['model_type']}
        """)
    
    # Route to pages
    if "Home" in page:
        from frontend.pages import home
        home.show()
    
    elif "Dashboard" in page:
        from frontend.pages import dashboard
        dashboard.show()
    
    elif "Prediction" in page:
        from frontend.pages import prediction
        prediction.show()
    
    elif "Charts" in page:
        from frontend.pages import charts
        charts.show()
    
    elif "AI Insights" in page:
        from frontend.pages import ai_insights
        ai_insights.show()
    
    elif "About" in page:
        from frontend.pages import about
        about.show()


if __name__ == "__main__":
    main()
