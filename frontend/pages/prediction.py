"""
Prediction Page
AI predictions and trading signals
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from backend.config import INDIAN_COMPANIES, THEME, THRESHOLD_OPTIONS, DEFAULT_THRESHOLD, STREAMLIT_CLOUD_MODE
from backend.utils.data_fetcher import DataFetcher
from backend.utils.features import FeatureEngineer
from backend.utils.model_predictor import ModelPredictor


def select_display_prediction(analysis, fallback_prediction=None):
    """Prefer the live-price-aligned prediction from full analysis."""
    if isinstance(analysis, dict) and isinstance(analysis.get("prediction"), dict):
        return analysis["prediction"]
    return fallback_prediction


def show():
    """Display Prediction page"""
    
    st.markdown("# 🔮 AI Prediction & Trading Signals")
    st.markdown("Get intelligent trading recommendations powered by Machine Learning")
    
    # Check if company is selected
    selected_company = st.session_state.get('selected_company')
    if selected_company is None:
        st.warning("⚠️ Please select a company from the Dashboard first!")
        st.info("Go to Dashboard → Select a company → Return here")
        return
    
    # Get current selection from session safely
    company_name = selected_company
    exchange = st.session_state.get('selected_exchange')
    ticker = st.session_state.get('current_ticker')
    live_data = st.session_state.get('live_data')
    
    if ticker is None:
        st.error("No ticker found. Please select a company from Dashboard.")
        return
    
    st.markdown("---")
    
    # Company Info Header
    st.markdown(f"## Selected: {company_name} ({exchange})")
    st.markdown(f"**Ticker:** `{ticker}`")
    
    st.markdown("---")
    
    # Threshold Selection
    st.markdown("### ⚙️ Prediction Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        threshold_name = st.selectbox(
            "Prediction Threshold",
            list(THRESHOLD_OPTIONS.keys()),
            help="Higher threshold = stricter buy/sell conditions"
        )
        threshold_value = THRESHOLD_OPTIONS[threshold_name]
    
    with col2:
        st.info(f"""
        **Threshold:** {threshold_name}
        
        This controls how strong the expected move must be before a BUY/SELL signal is shown.
        Higher values make the system more conservative.
        """)

    try:
        fetcher = DataFetcher()

        # Fetch historical data
        hist_data = fetcher.fetch_historical_data(ticker, days=365)

        if hist_data is None:
            st.error("Could not fetch historical data")
            return

        # Check data source and display appropriate indicator
        is_historical_demo = isinstance(hist_data, pd.DataFrame) and len(hist_data) < 100
        if is_historical_demo:
           st.warning("""
           ⚠️ **IMPORTANT: Synthetic Data Warning**
            
           Real historical data is unavailable for this stock. 
           This model is being trained on **synthetic, artificially generated data**.
            
           **⚠️ Predictions based on synthetic data are NOT reliable for actual trading decisions.**
            
           Consider this for demonstration purposes only.
           """)
        else:
           st.success("✓ **Real Historical Data** - Model trained on actual market data")

        # Prepare features
        engineer = FeatureEngineer(hist_data)
        features_df = engineer.prepare_features()

        # Initialize predictor
        predictor = ModelPredictor(company_name, ticker)

        # Try to load model. If it is missing or incompatible, either train a fresh one
        # or (when STREAMLIT_CLOUD_MODE is enabled) use a lightweight demo heuristic.
        cloud_demo = False
        if not predictor.load_model():
            if STREAMLIT_CLOUD_MODE:
                cloud_demo = True
                st.info("Model file not found. Using lightweight demo prediction (Streamlit Cloud safe).")
                # Use a simple recent-returns mean as a demo predicted return
                last_close = float(hist_data['Close'].iloc[-1]) if 'Close' in hist_data.columns else None
                if last_close is None:
                    st.error("No close price available to produce a demo prediction.")
                    return
                predicted_return = 0.0
                if 'Return' in features_df.columns:
                    recent = features_df['Return'].dropna().tail(20)
                    if len(recent) > 0:
                        predicted_return = float(recent.mean())
                predicted_price = last_close * (1.0 + predicted_return)
                prediction = {
                    'predicted_return': predicted_return,
                    'predicted_price': predicted_price,
                    'current_price': last_close,
                    'price_change': predicted_price - last_close,
                    'change_percent': predicted_return * 100,
                }

                # Simple advisory signal based on threshold_value
                if predicted_return > threshold_value:
                    signal_type = 'BUY'
                    recommendation = f"Predicted return {predicted_return:.2%} > threshold"
                elif predicted_return < -threshold_value:
                    signal_type = 'SELL'
                    recommendation = f"Predicted return {predicted_return:.2%} < -threshold"
                else:
                    signal_type = 'HOLD'
                    recommendation = f"Predicted return {predicted_return:.2%} near threshold"

                analysis = {
                    'prediction': prediction,
                    'signal': {
                        'signal': signal_type,
                        'recommendation': recommendation,
                        'reason': 'Demo heuristic (recent returns mean) because model file is unavailable.',
                        'confidence': max(0.01, min(0.5, abs(predicted_return)))
                    },
                    'targets': {
                        'entry_price': last_close,
                        'target_price': predicted_price,
                        'conservative_target': last_close * (1 + predicted_return * 0.5),
                        'aggressive_target': last_close * (1 + predicted_return * 1.5),
                        'stop_loss': last_close * (1 - abs(predicted_return) * 1.0),
                    }
                }
            else:
                st.info("Training a fresh model for this stock because the previous model was missing or incompatible...")
                X, y = predictor.trainer.prepare_training_data(features_df)
                if len(X) > 50:
                    predictor.trainer.train_model(X, y)
                    predictor.trainer.save_model()
                else:
                    st.error("Not enough data to train model")
                    return

        # If not in cloud_demo mode, make prediction using the model
        if not cloud_demo:
            # Make prediction using the latest market price when available.
            live_current_price = None
            if live_data is not None and isinstance(live_data, dict):
                try:
                    live_current_price = float(live_data.get("current_price"))
                except (TypeError, ValueError):
                    live_current_price = None

            prediction = predictor.predict_next_price(
                features_df,
                current_price_override=live_current_price,
                latest_volatility=float(features_df.iloc[-1]["Volatility"]) if "Volatility" in features_df.columns else None,
            )

            if live_current_price is not None and prediction is not None:
                prediction["current_price"] = live_current_price
                prediction["predicted_price"] = live_current_price * (1 + prediction.get("predicted_return", 0.0))
                prediction["price_change"] = prediction["predicted_price"] - live_current_price
                prediction["change_percent"] = prediction.get("predicted_return", 0.0) * 100

            if prediction is None:
                st.error("Could not make prediction")
                return

            # Get full analysis
            analysis = predictor.get_full_analysis(features_df, live_data, threshold_value)
            if analysis is None:
                st.error("Could not generate a full prediction analysis at this time. Please try again later.")
                return
            prediction = select_display_prediction(analysis, prediction)
        else:
            # cloud_demo has created 'analysis' and 'prediction' already
            pass

        st.markdown("---")

        # PREDICTION RESULTS
        st.markdown("## 📊 Prediction Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Price",
                f"₹{prediction['current_price']:.2f}",
                help="Latest closing price"
            )

        with col2:
            delta_text = f"{prediction['change_percent']:+.2f}%"
            st.metric(
                "Predicted Price",
                f"₹{prediction['predicted_price']:.2f}",
                delta_text,
                help="Expected price for next trading day"
            )

        with col3:
            st.metric(
                "Expected Return",
                f"{prediction['change_percent']:.2f}%",
                help="Predicted percentage change"
            )

        st.markdown("---")

        # TRADING SIGNAL
        st.markdown("## 🎯 Trading Signal")

        signal_data = analysis.get('signal', {})
        prediction_data = analysis.get('prediction', prediction)

        # Color based on signal
        signal_colors = {
            'BUY': '🟢 #2ca02c',
            'SELL': '🔴 #d62728',
            'HOLD': '🟡 #ff9800'
        }

        col1, col2 = st.columns([1, 2])

        with col1:
            signal_type = signal_data.get('signal', 'HOLD')
            signal_emoji, signal_color = signal_colors.get(signal_type, '🟡 #ff9800').split()
            signal_color = signal_color if signal_color else 'f59e0b'

            st.markdown(
                f"<div style='background-color:#161b22; border-left:8px solid #{signal_color}; padding:1.5rem; border-radius:0.5rem; text-align:center;'>"
                f"<h1 style='color:#ffffff; font-size:2.5rem; margin:0;'>{signal_emoji}</h1>"
                f"<h2 style='color:#ffffff; font-size:1.6rem; margin:0.4rem 0;'>{signal_type}</h2>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col2:
            threshold_percent = threshold_value * 100
            recommendation = signal_data.get('recommendation', 'No recommendation available.')
            reason = signal_data.get('reason', 'No reason provided.')
            confidence = signal_data.get('confidence', 0.0)
            message = (
                f"**Recommendation:** {recommendation}\n\n"
                f"**Reason:** {reason}\n\n"
                f"**Confidence:** {confidence:.1%}\n\n"
                f"**Threshold Used:** {threshold_name} ({threshold_percent:.2f}%)"
            )
            st.markdown(message)
            st.caption("Changing this threshold will change the BUY/SELL/HOLD decision when the expected move is near the cutoff.")

        st.markdown("---")

        # PRICE TARGETS AND STOP LOSS
        st.markdown("## 🎯 Price Targets")
        
        targets = analysis.get('targets', {})
        if targets:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Entry Price:** ₹{targets.get('entry_price', 0.0):.2f}")
                st.markdown(f"**Target Price:** ₹{targets.get('target_price', 0.0):.2f}")
            with col2:
                st.markdown(f"**Conservative Target:** ₹{targets.get('conservative_target', 0.0):.2f}")
                st.markdown(f"**Aggressive Target:** ₹{targets.get('aggressive_target', 0.0):.2f}")
            with col3:
                st.markdown(f"**Stop Loss:** ₹{targets.get('stop_loss', 0.0):.2f}")
                st.markdown(f"**Risk/Reward:** {targets.get('risk_reward_ratio', 0.0):.2f}")
        else:
            st.info("Price targets are not available for this analysis.")
        
        st.markdown("---")
        
        # TECHNICAL INDICATORS
        st.markdown("## 📈 Technical Indicators")
        
        indicators = analysis.get('indicators', {})
        if not indicators:
            indicators = FeatureEngineer(features_df).get_latest_indicators()

        col1, col2, col3 = st.columns(3)

        with col1:
            message = (
                "**Moving Averages**\n\n"
                f"MA10: Rs {indicators['MA10']:.2f}\n\n"
                f"MA20: Rs {indicators['MA20']:.2f}\n\n"
                f"Current: Rs {indicators['Close']:.2f}"
            )
            st.markdown(message)

        with col2:
            if indicators['RSI'] < 70 and indicators['RSI'] > 30:
                status_text = "📈 Bullish"
            elif indicators['RSI'] >= 70:
                status_text = "🔴 Overbought"
            else:
                status_text = "🟢 Oversold"

            message = (
                "**Momentum (RSI)**\n\n"
                f"RSI: {indicators['RSI']:.2f}\n\n"
                f"Status: {status_text}"
            )
            st.markdown(message)

        with col3:
            message = (
                "**MACD**\n\n"
                f"MACD: {indicators['MACD']:.4f}\n\n"
                f"Signal: {indicators['MACD_Signal']:.4f}\n\n"
                f"Hist: {indicators['MACD_Hist']:.4f}"
            )
            st.markdown(message)

        st.markdown("---")

        # RISK ASSESSMENT
        st.markdown("## ⚠️ Risk Assessment")

        risk = analysis.get('risk', {
            'risk_level': 'LOW',
            'risk_score': 0.0,
            'risk_emoji': '✅',
            'risk_factors': ['Insufficient data']
        })

        col1, col2 = st.columns([1, 2])

        with col1:
            risk_colors = {
                'LOW': '#2ca02c',
                'MEDIUM': '#ff9800',
                'HIGH': '#d62728'
            }
            risk_color = risk_colors.get(risk['risk_level'], '#f59e0b')
            st.markdown(
                f"<div style='background-color:#161b22; border-left:8px solid {risk_color}; padding:1.5rem; border-radius:0.5rem; text-align:center;'>"
                f"<h3 style='color:#ffffff; margin:0;'>Risk Level</h3>"
                f"<h2 style='color:{risk_color}; font-size:1.8rem; margin:0.4rem 0;'>{risk['risk_emoji']}</h2>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col2:
            risk_message = (
                f"**Risk Score:** {risk['risk_score']:.2f} / 1.00\n\n"
                "**Risk Factors:**"
            )
            st.markdown(risk_message)
            for factor in risk['risk_factors']:
                st.markdown(f"- {factor}")

        st.markdown("---")

        # DETAILED METRICS
        st.markdown("## 📋 Detailed Metrics")

        metrics_data = {
            'Metric': [
                'Current Price',
                'Predicted Price',
                'Price Change',
                'Change %',
                'MA10',
                'MA20',
                'RSI',
                'Volatility',
                'Daily Return',
                'BB High',
                'BB Low',
                'Confidence',
                'Prediction Time'
            ],
            'Value': [
                f"₹{prediction_data['current_price']:.2f}",
                f"₹{prediction_data['predicted_price']:.2f}",
                f"{prediction_data['change_percent']:+.2f}%",
                f"{prediction_data['change_percent']:.2f}%",
                f"₹{indicators['MA10']:.2f}",
                f"₹{indicators['MA20']:.2f}",
                f"{indicators['RSI']:.2f}",
                f"{indicators['Volatility']:.6f}",
                f"{indicators['Daily_Return']:.4f}",
                f"₹{indicators['BB_High']:.2f}",
                f"₹{indicators['BB_Low']:.2f}",
                f"{prediction_data['confidence']:.2%}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }

        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, width="stretch")

        st.markdown("---")

        # DISCLAIMER
        st.warning(
            "**Important Disclaimer:**\n\n"
            "- This prediction is based on historical data and machine learning\n"
            "- Past performance does not guarantee future results\n"
            "- Always conduct your own research before investing\n"
            "- Consult with a financial advisor for investment decisions\n"
            "- Stock market is inherently risky and unpredictable"
        )

        st.markdown("---")

        # Navigation Tips
        col1, col2 = st.columns(2)

        with col1:
            st.info(
                "**Next Steps:**\n\n"
                "1. View Charts -> Technical analysis visualization\n"
                "2. Check AI Insights -> Model explanation\n"
                "3. Select different threshold to see signal changes"
            )

        with col2:
            st.success(
                "**How to Use Signals:**\n\n"
                "- BUY: Expected gain > threshold\n"
                "- SELL: Expected loss > threshold\n"
                "- HOLD: Change within threshold"
            )

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Make sure the company data is available and try refreshing the dashboard.")
