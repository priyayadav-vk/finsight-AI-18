"""
About Page
Project documentation and team details
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from backend.config import *


def show():
    """Display About page"""
    
    st.markdown("# ℹ️ About FinSight AI")
    st.markdown("A comprehensive guide to the project")
    
    st.markdown("---")
    
    # Project Overview
    st.markdown("## 📋 Project Overview")
    
    st.markdown(f"""
    **Project Name:** {PROJECT_NAME}
    
    **Subtitle:** {PROJECT_SUBTITLE}
    
    **Version:** {VERSION}
    
    **Project Type:** {PROJECT_TYPE}
    
    ### Description:
    
    FinSight AI is an **Intelligent Stock Market Prediction & Investment Assistant**
    developed as a **Project**. It leverages cutting-edge machine learning
    techniques, real-time market data, and comprehensive technical analysis to predict
    stock prices and generate automated trading signals.
    
    The project demonstrates practical application of:
    - Machine Learning (Random Forest Algorithm)
    - Technical Analysis (10+ indicators)
    - Web Development (Streamlit)
    - Real-time Data Processing
    - Financial Analysis
    """)
    
    st.markdown("---")
    
    # Project Objectives
    st.markdown("## 🎓 Project Objectives")
    
    objectives = {
        'Objective': [
            'Stock Price Prediction',
            'Trading Signal Generation',
            'Risk Assessment',
            'Technical Analysis',
            'User Interface Design',
            'Real-time Updates',
            'Model Explainability'
        ],
        'Description': [
            'Use ML to predict next day closing price',
            'Generate BUY/HOLD/SELL recommendations',
            'Assess investment risk levels',
            'Calculate 10+ technical indicators',
            'Create user-friendly web application',
            'Fetch live market data from Yahoo Finance',
            'Explain model decisions transparently'
        ],
        'Status': ['✅ Complete'] * 7
    }
    
    obj_df = st.dataframe(objectives)
    
    st.markdown("---")
    
    # Technology Stack
    st.markdown("## 🛠️ Technology Stack")
    
    st.markdown("""
    - **Python** - Core language
    - **Scikit-Learn** - Random Forest ML
    - **Streamlit** - Web framework
    - **Plotly** - Interactive charts
    - **Pandas & NumPy** - Data processing
    - **yfinance** - Live market data
    - **TA** - Technical indicators
    """)
    
    st.markdown("---")
    
    # Workflow & Architecture
    st.markdown("## 🔄 System Workflow")
    
    st.markdown("""
    ### Data Pipeline:
    
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                      USER INTERACTION                        │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
    │  │   Dashboard  │  │  Prediction  │  │    Charts    │      │
    │  └──────────────┘  └──────────────┘  └──────────────┘      │
    └─────────────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │                    STREAMLIT APP                            │
    │  app.py - Main application with page routing               │
    └─────────────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │                  BACKEND MODULES                            │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ 1. Data Fetcher                                     │   │
    │  │    → Fetch live data from Yahoo Finance            │   │
    │  │    → Store historical data                         │   │
    │  └─────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ 2. Feature Engineering                              │   │
    │  │    → Calculate MA10, MA20, RSI, MACD, etc          │   │
    │  │    → Prepare data for ML                           │   │
    │  └─────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ 3. Model Training                                   │   │
    │  │    → Train Random Forest (100 trees)               │   │
    │  │    → Save models with Joblib                       │   │
    │  └─────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ 4. Model Predictor                                  │   │
    │  │    → Load trained models                           │   │
    │  │    → Make predictions                              │   │
    │  │    → Generate signals & risk assessment            │   │
    │  └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘
    ```
    """)
    
    st.markdown("---")
    
    # Future Scope
    st.markdown("## 🚀 Future Scope & Enhancements")
    
    future_features = {
        'Feature': [
            'Multiple ML Models',
            'Ensemble Methods',
            'Fundamental Analysis',
            'Sentiment Analysis',
            'Portfolio Management',
            'Risk Calculation',
            'Backtesting Engine',
            'Mobile App',
            'API Development',
            'Database Integration',
            'Real-time Notifications',
            'Advanced Visualizations'
        ],
        'Description': [
            'XGBoost, LightGBM, Neural Networks',
            'Combine predictions from multiple models',
            'P/E ratio, earnings, dividend analysis',
            'News & social media sentiment',
            'Portfolio optimization & allocation',
            'VaR, Sharpe ratio calculations',
            'Historical strategy testing',
            'iOS/Android application',
            'REST API for integration',
            'Store data for analytics',
            'Alerts on price movements',
            'Advanced Plotly features'
        ]
    }
    
    future_df = pd.DataFrame(future_features)
    st.dataframe(future_df)
    
    st.markdown("---")
    
    # Team
    st.markdown("## 👥 Team Members")
    
    st.markdown(f"""
    {chr(10).join([f'• **{member}**' for member in TEAM_MEMBERS])}
    """)

    st.markdown("### Guide")
    st.markdown("**Mr. Rajeshvar Gupta**")
    
    st.markdown("---")
    
    # Institution Details
    st.markdown("## 🎓 Institution Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        ### College
        
        **{COLLEGE}**
        
        A premier engineering institution dedicated to excellence
        in technical education and research.
        """)
    
    with col2:
        st.markdown(f"""
        ### Course Details
        
        **Degree:** {COURSE}
        
        **Project Type:** {PROJECT_TYPE}
        
        **Subject:** AI & Machine Learning
        
        **Duration:** 2026
        """)
    
    st.markdown("---")
    
    # Key Features Summary
    st.markdown("## ✨ Key Features")
    
    features_text = """
    ### Core Features:
    ✅ AI-powered stock price predictions
    ✅ Automated BUY/HOLD/SELL signals
    ✅ Real-time market data from Yahoo Finance
    ✅ 10+ technical indicators calculation
    ✅ Risk assessment and confidence scores
    ✅ Interactive Plotly charts
    ✅ 144+ Indian companies supported
    ✅ Both NSE and BSE listings
    ✅ Model explainability
    ✅ Clean, intuitive UI
    
    ### Advanced Features:
    🔧 Customizable prediction thresholds
    🔧 Feature importance visualization
    🔧 Technical analysis education
    🔧 Session state management
    🔧 Prediction history tracking
    🔧 Multi-exchange support
    🔧 Responsive design
    """
    
    st.markdown(features_text)
    
    st.markdown("---")
    
    # How to Use
    st.markdown("## 📖 Quick Start")
    
    st.markdown("""
    1. **Dashboard** - Select a company and view data
    2. **Prediction** - Get AI signals
    3. **Charts** - Analyze technical patterns
    4. **AI Insights** - Learn about the model
    """)
    
    st.markdown("---")
    
    # Contact & Support
    st.markdown("## 📞 Contact & Support")
    
    st.info("""
    ### Questions or Feedback?
    
    For issues, suggestions, or questions:
    
    📧 **Email:** priyayadav45937@gmail.com
    
    We appreciate your feedback and suggestions!
    """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #8b949e; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #30363d;">
        <p>
            <strong>FinSight AI v1.0.0</strong><br>
            Project - Intelligent Stock Market Prediction & Investment Assistant<br>
            Rajasthan College of Engineering for Women<br>
            <br>
            © 2024 All Rights Reserved | Made with ❤️ using Streamlit & Machine Learning
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show()
