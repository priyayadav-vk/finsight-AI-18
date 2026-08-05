"""
Dashboard Page
Company selection and live market data display
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from config import INDIAN_COMPANIES, THEME, FEATURED_COMPANIES
from utils.data_fetcher import DataFetcher


def show():
    """Display Dashboard page"""
    
    # Top section removed per user request — start directly at Company Selection
    # Initialize DataFetcher (used later for refresh and live data)
    fetcher = DataFetcher()

    # Company Selection Section (page begins here)
    st.markdown("## 🔍 Company Selection")

    # Keep the dashboard scoped to the Indian company universe.
    st.caption("Showing the Indian company universe.")

    # Prefer the live-supported company set for the dropdown and feature picks.
    try:
        if hasattr(fetcher, 'get_supported_companies'):
            live_supported_companies = fetcher.get_supported_companies(force_refresh=False, universe='indian')
        else:
            # Defensive fallback for older DataFetcher implementations
            live_supported_companies = None
    except Exception:
        live_supported_companies = None
    active_company_map = live_supported_companies if live_supported_companies else INDIAN_COMPANIES
    companies_list = sorted(list(active_company_map.keys()))
    if not companies_list:
        st.warning("No companies are currently configured.")
        return

    # Featured quick-pick (show only featured companies validated as available)
    featured_choice = None
    if FEATURED_COMPANIES:
        # Show featured companies that exist in the current companies list
        featured_available = [c for c in FEATURED_COMPANIES if c in active_company_map]
        featured_unavailable = [c for c in FEATURED_COMPANIES if c not in companies_list]
        if featured_available:
            featured_choice = st.selectbox(
                label="Quick pick featured company",
                options=[""] + featured_available,
                index=0,
                help="Pick a featured blue-chip company"
            )
            if featured_choice == "":
                featured_choice = None
        else:
            # If no featured companies are present, show a neutral message
            st.info("No featured companies are currently present in the registry.")
            if featured_unavailable:
                st.caption(f"Featured but missing from registry: {', '.join(featured_unavailable[:6])}{(' and more' if len(featured_unavailable)>6 else '')}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Company search & selection (only shown when no featured quick-pick chosen)
        if featured_choice:
            selected_company = featured_choice
            st.markdown(f"Selected featured company: **{selected_company}**")
        else:
            selected_company = st.selectbox(
                label="Select or search company",
                options=companies_list,
                index=0,
                help="Search by company name or scroll through the list"
            )
    
    with col2:
        # Refresh button
        refresh_button = st.button("🔄 Refresh", width="stretch")
    
    if refresh_button:
        try:
            if hasattr(fetcher, 'get_supported_companies'):
                live_supported_companies = fetcher.get_supported_companies(force_refresh=True, universe='indian')
            else:
                live_supported_companies = None
        except Exception:
            live_supported_companies = None
        active_company_map = live_supported_companies if live_supported_companies else INDIAN_COMPANIES
        companies_list = sorted(list(active_company_map.keys()))

    # Store in session state
    st.session_state.selected_company = selected_company
    
    if selected_company is None:
        st.warning("Please select a company first")
        return
    
    # Get company info
    company_info = active_company_map[selected_company]
    st.session_state.selected_exchange = st.selectbox(
        "Select Exchange",
        ["NSE", "BSE"],
        help="NSE - National Stock Exchange, BSE - Bombay Stock Exchange"
    )
    
    # Get ticker for selected exchange
    if st.session_state.selected_exchange == "NSE":
        ticker = company_info['NSE']
    else:
        ticker = company_info['BSE']
    
    st.session_state.current_ticker = ticker
    
    st.markdown("---")
    
    # Fetch live data
    st.markdown("## 📈 Live Market Data")
     
    with st.spinner("Fetching live data..."):
        try:
            live_data = fetcher.fetch_live_data(ticker)
             
            if live_data is None:
                st.error(f"Could not fetch data for {ticker}")
                st.info("The stock market may be closed or the ticker is unavailable.")
                return
             
            # Display data source indicator
            if live_data.get('is_demo'):
                data_source = live_data.get('data_source', 'Synthetic Data')
                st.warning(f"""
                ⚠️ **Data Source Alert**: {data_source}
                 
                Real-time Yahoo Finance data is currently unavailable for {ticker}.
                The displayed data is synthetically generated for demonstration purposes.
                **Predictions and analysis based on this data may not be reliable.**
                """)
            else:
                st.success(f"""
                ✓ **Real-Time Data**: Yahoo Finance
                 
                Source: {live_data.get('data_source', 'Yahoo Finance')}
                """)
             
            # Store in session state for other pages
            st.session_state.live_data = live_data
            
            # Display company info header
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {live_data['company_name']}")
                st.markdown(f"**Ticker:** `{ticker}` | **Exchange:** {st.session_state.selected_exchange}")
            
            with col2:
                st.markdown("**Market Status**")
                st.markdown(f"# {live_data['market_status']}")
            
            with col3:
                st.markdown("**Last Updated**")
                st.markdown(f"`{live_data['last_updated']}`")
            
            st.markdown("---")
            
            # Main metrics
            st.markdown("### Current Market Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Current Price",
                    value=f"₹{live_data['current_price']:.2f}",
                    delta=f"₹{(live_data['current_price'] - live_data['previous_close']):.2f}",
                    delta_color="normal"
                )
            
            with col2:
                change_percent = ((live_data['current_price'] - live_data['previous_close']) / 
                                 live_data['previous_close'] * 100)
                st.metric(
                    label="Change %",
                    value=f"{change_percent:.2f}%",
                    delta=f"{abs(change_percent):.2f}%"
                )
            
            with col3:
                st.metric(
                    label="Today's High",
                    value=f"₹{live_data['high_price']:.2f}"
                )
            
            with col4:
                st.metric(
                    label="Today's Low",
                    value=f"₹{live_data['low_price']:.2f}"
                )
            
            st.markdown("---")
            
            # Additional details
            st.markdown("### Additional Details")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                **Opening Price**
                
                ₹{live_data['open_price']:.2f}
                """)
            
            with col2:
                st.markdown(f"""
                **Previous Close**
                
                ₹{live_data['previous_close']:.2f}
                """)
            
            with col3:
                st.markdown(f"""
                **Trading Volume**
                
                {live_data['volume']:,}
                """)
            
            with col4:
                st.markdown(f"""
                **Sector**
                
                {company_info.get('sector', 'N/A')}
                """)
            
            st.markdown("---")
            
            # Data summary table
            st.markdown("### Data Summary")
            
            data_summary = pd.DataFrame({
                'Metric': [
                    'Current Price',
                    'Open',
                    'High',
                    'Low',
                    'Previous Close',
                    'Volume',
                    'Market Status',
                    'Last Updated'
                ],
                'Value': [
                    f"₹{live_data['current_price']:.2f}",
                    f"₹{live_data['open_price']:.2f}",
                    f"₹{live_data['high_price']:.2f}",
                    f"₹{live_data['low_price']:.2f}",
                    f"₹{live_data['previous_close']:.2f}",
                    f"{live_data['volume']:,}",
                    live_data['market_status'],
                    live_data['last_updated']
                ]
            })
            
            st.dataframe(data_summary, width="stretch")
            
            st.markdown("---")
            
            # Info boxes
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **ℹ️ Company Information**
                
                **Name:** {live_data['company_name']}
                
                **Ticker:** {ticker}
                
                **Exchange:** {st.session_state.selected_exchange}
                
                **Sector:** {company_info.get('sector', 'N/A')}
                """)
            
            with col2:
                st.success(f"""
                **✅ Quick Navigation**
                
                1. Go to **Prediction** → Get AI signals
                
                2. Go to **Charts** → See technical analysis
                
                3. Go to **AI Insights** → Learn about the model
                """)
            
            st.markdown("---")
            
            # Pro tips
            st.markdown("### 💡 Dashboard Tips")
            
            tips = """
            - **Refresh Data:** Click the 🔄 Refresh button to get the latest prices
            - **Change Company:** Use the dropdown to switch between companies
            - **Exchange Toggle:** Switch between NSE and BSE listings
            - **Next Steps:** Use the Prediction page for AI signals
            - **Save Favorites:** (Coming soon) Add companies to your watchlist
            """
            
            st.markdown(tips)
            
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Make sure you have an internet connection and Yahoo Finance is accessible.")


if __name__ == "__main__":
    show()
