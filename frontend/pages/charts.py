"""
Charts Page
Interactive technical analysis charts
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from backend.config import CHART_COLORS
from backend.utils.data_fetcher import DataFetcher
from backend.utils.features import FeatureEngineer


def create_candlestick_chart(df):
    """Create candlestick chart"""
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    )])
    
    fig.update_layout(
        title='Candlestick Chart - Price Movement',
        yaxis_title='Stock Price (₹)',
        xaxis_title='Date',
        template='plotly_dark',
        height=500,
        hovermode='x unified'
    )
    
    return fig


def create_volume_chart(df):
    """Create volume chart"""
    
    colors = [CHART_COLORS['bullish'] if df.iloc[i]['Close'] >= df.iloc[i]['Open'] 
              else CHART_COLORS['bearish'] for i in range(len(df))]
    
    fig = go.Figure(data=[go.Bar(
        x=df['Date'],
        y=df['Volume'],
        marker_color=colors,
        name='Volume'
    )])
    
    fig.update_layout(
        title='Trading Volume',
        yaxis_title='Volume',
        xaxis_title='Date',
        template='plotly_dark',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_moving_average_chart(df):
    """Create moving average chart with price"""
    
    fig = go.Figure()
    
    # Close price
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # MA10
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MA10'],
        mode='lines',
        name='MA10',
        line=dict(color='#ff7f0e', width=1.5, dash='dash')
    ))
    
    # MA20
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MA20'],
        mode='lines',
        name='MA20',
        line=dict(color='#d62728', width=1.5, dash='dash')
    ))
    
    fig.update_layout(
        title='Price with Moving Averages',
        yaxis_title='Price (₹)',
        xaxis_title='Date',
        template='plotly_dark',
        height=500,
        hovermode='x unified'
    )
    
    return fig


def create_rsi_chart(df):
    """Create RSI indicator chart"""
    
    fig = go.Figure()
    
    # RSI line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Overbought line (70)
    fig.add_hline(y=70, line_dash="dash", line_color="#d62728",
                  annotation_text="Overbought (70)", annotation_position="right")
    
    # Oversold line (30)
    fig.add_hline(y=30, line_dash="dash", line_color="#2ca02c",
                  annotation_text="Oversold (30)", annotation_position="right")
    
    # Neutral zone (50)
    fig.add_hline(y=50, line_dash="dot", line_color="#8b949e")
    
    fig.update_layout(
        title='RSI (Relative Strength Index) - Momentum Indicator',
        yaxis_title='RSI (0-100)',
        xaxis_title='Date',
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        yaxis=dict(range=[0, 100])
    )
    
    return fig


def create_macd_chart(df):
    """Create MACD chart"""
    
    colors = [CHART_COLORS['bullish'] if df.iloc[i]['MACD_Hist'] >= 0 
              else CHART_COLORS['bearish'] for i in range(len(df))]
    
    fig = go.Figure()
    
    # MACD line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Signal line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MACD_Signal'],
        mode='lines',
        name='Signal',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    # Histogram
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['MACD_Hist'],
        name='Histogram',
        marker_color=colors,
        opacity=0.5
    ))
    
    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="#8b949e")
    
    fig.update_layout(
        title='MACD (Moving Average Convergence Divergence)',
        yaxis_title='MACD Value',
        xaxis_title='Date',
        template='plotly_dark',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_bollinger_bands_chart(df):
    """Create Bollinger Bands chart"""
    
    fig = go.Figure()
    
    # Close price
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Upper band
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['BB_High'],
        mode='lines',
        name='Upper Band',
        line=dict(color='#d62728', width=1, dash='dash')
    ))
    
    # Middle band
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['BB_Middle'],
        mode='lines',
        name='Middle Band',
        line=dict(color='#8b949e', width=1, dash='dot')
    ))
    
    # Lower band
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['BB_Low'],
        mode='lines',
        name='Lower Band',
        line=dict(color='#2ca02c', width=1, dash='dash'),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='Bollinger Bands - Support & Resistance',
        yaxis_title='Price (₹)',
        xaxis_title='Date',
        template='plotly_dark',
        height=500,
        hovermode='x unified'
    )
    
    return fig


def create_volatility_chart(df):
    """Create volatility chart"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Volatility'],
        mode='lines',
        name='Volatility',
        line=dict(color='#ff7f0e', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Historical Volatility (20-day Standard Deviation)',
        yaxis_title='Volatility',
        xaxis_title='Date',
        template='plotly_dark',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def show():
    """Display Charts page"""
    
    st.markdown("# 📈 Technical Analysis Charts")
    st.markdown("Interactive visualizations of technical indicators")
    
    # Check if company is selected
    if st.session_state.selected_company is None:
        st.warning("⚠️ Please select a company from the Dashboard first!")
        return
    
    company_name = st.session_state.selected_company
    ticker = st.session_state.current_ticker
    
    st.markdown(f"## {company_name} ({ticker})")
    
    st.markdown("---")
    
    # Chart selection
    chart_type = st.selectbox(
        "Select Chart",
        [
            "📊 Candlestick Chart",
            "📈 Volume Chart",
            "📉 Moving Averages",
            "💪 RSI (Momentum)",
            "🔄 MACD",
            "📊 Volatility"
        ]
    )
    
    with st.spinner("Loading chart data..."):
        try:
            # Fetch data
            fetcher = DataFetcher()
            hist_data = fetcher.fetch_historical_data(ticker, days=365)
             
            if hist_data is None:
                st.error("Could not fetch historical data")
                return
             
            # Check data source and display appropriate indicator
            is_historical_demo = isinstance(hist_data, pd.DataFrame) and len(hist_data) < 100
            if is_historical_demo:
               st.warning("""
               ⚠️ **Data Source Alert**: Synthetic Historical Data
                
               Real historical data is unavailable for this stock.
               Charts are based on synthetically generated data for demonstration.
               **Analysis based on this data may not be reliable.**
               """)
            else:
               st.success("✓ **Real Historical Data** - Yahoo Finance")
             
            # Prepare features
            engineer = FeatureEngineer(hist_data)
            features_df = engineer.prepare_features()
            
            # Display selected chart
            if "Candlestick" in chart_type:
                fig = create_candlestick_chart(features_df)
            
            elif "Volume" in chart_type:
                fig = create_volume_chart(features_df)
            
            elif "Moving" in chart_type:
                fig = create_moving_average_chart(features_df)
            
            elif "RSI" in chart_type:
                fig = create_rsi_chart(features_df)
            
            elif "MACD" in chart_type:
                fig = create_macd_chart(features_df)
            
            elif "Volatility" in chart_type:
                fig = create_volatility_chart(features_df)
            
            # Display chart
            st.plotly_chart(fig, width="stretch")
            
            st.markdown("---")
            
            # Chart description
            descriptions = {
                "Candlestick": """
                **Candlestick Chart** shows OHLC (Open, High, Low, Close) data:
                - Green candle = Price up
                - Red candle = Price down
                - Useful for identifying trends and reversals
                """,
                "Volume": """
                **Volume Chart** shows trading activity:
                - Green bars = Buying pressure
                - Red bars = Selling pressure
                - High volume confirms trends
                """,
                "Moving": """
                **Moving Averages**:
                - MA10 = Short-term trend (10 days)
                - MA20 = Medium-term trend (20 days)
                - Crossover = Potential signal
                """,
                "RSI": """
                **RSI (Relative Strength Index)**:
                - Range: 0-100
                - > 70 = Overbought (potential sell)
                - < 30 = Oversold (potential buy)
                - 30-70 = Neutral zone
                """,
                "MACD": """
                **MACD (Moving Average Convergence Divergence)**:
                - MACD > Signal = Bullish
                - MACD < Signal = Bearish
                - Histogram = Strength of signal
                """,
                "Volatility": """
                **Historical Volatility**:
                - Measures price stability
                - High volatility = High risk/reward
                - Low volatility = Stable price
                - Important for risk assessment
                """
            }
            
            for key, desc in descriptions.items():
                if key in chart_type:
                    st.info(desc)
            
            st.markdown("---")
            
            # Data table
            if st.checkbox("Show raw data"):
                st.dataframe(features_df.tail(20), width="stretch")
        
        except Exception as e:
            st.error(f"Error loading charts: {str(e)}")


if __name__ == "__main__":
    show()
