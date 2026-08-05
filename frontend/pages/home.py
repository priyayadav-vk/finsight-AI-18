"""
Home Page
Beautiful landing page with project information
"""

import streamlit as st
from backend.config import *


def show():
    """Display Home page"""
    
    # Hero Section
    st.markdown("---")
    
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1d4ed8 0%, #64748b 100%);
            padding: 1.5rem 1.4rem;
            border-radius: 0.75rem;
            text-align: left;
            margin-bottom: 1.5rem;
            max-width: 720px;
            margin-left: auto;
            margin-right: auto;
        ">
            <h1 style="color: white; font-size: 2rem; margin: 0;">📈 FinSight AI</h1>
            <h2 style="color: #f8fafc; font-size: 1.05rem; font-weight: 400; margin: 0.5rem 0;">
                Intelligent Stock Market Prediction & Investment Assistant
            </h2>
            <p style="color: #f8fafc; margin-top: 0.8rem; font-size: 0.92rem;">
                Powered by Machine Learning • Real-time Market Data • Technical Analysis
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features
    st.markdown("## What You Can Do")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Predict
        - Next-day stock prediction
        - Confidence score
        - Simple signal output
        """)
    
    with col2:
        st.markdown("""
        ### Analyze
        - Live stock charts
        - Technical indicators
        - Market trend view
        """)
    
    with col3:
        st.markdown("""
        ### Decide
        - BUY / HOLD / SELL
        - Risk awareness
        - Faster decision support
        """)
    
    st.markdown("---")
    
    # Quick Start
    st.markdown("## Quick Start")
    
    st.info("""
    1. Open the Dashboard
    2. Pick a stock
    3. View prediction and signals
    4. Use Charts and AI Insights for more detail
    """)
    
    st.markdown("---")
    
    # Project Details
    st.markdown("## Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Safely construct team members list for display. This avoids IndexError
        # if TEAM_MEMBERS is missing, not a list, or empty.
        try:
            if isinstance(TEAM_MEMBERS, (list, tuple)) and len(TEAM_MEMBERS) > 0:
                members = TEAM_MEMBERS
            elif isinstance(DEVELOPER, str) and DEVELOPER.strip():
                members = [DEVELOPER]
            else:
                # Fallback default team members (safe defaults)
                members = ["Priya Yadav", "Diya Trisha", "Ojhal"]
        except Exception:
            members = ["Priya Yadav", "Diya Trisha", "Ojhal"]

        members_html = "".join([f"• {m}<br>" for m in members])
        st.markdown(f"""
        **Team:**
        {members_html}
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        **Institution:** {COLLEGE}
        
        **Course:** {COURSE}
        
        **Project Type:** {PROJECT_TYPE}
        """)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #8b949e; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #30363d;">
        <p>FinSight AI v1.0.0 | Project | Rajasthan College of Engineering for Women</p>
        <p>Made with Streamlit & Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show()
