"""
AI Insights Page
Machine Learning model explanation and metrics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from backend.config import FEATURE_INFO, MODEL_CONFIG
from backend.utils.data_fetcher import DataFetcher
from backend.utils.features import FeatureEngineer
from backend.utils.model_predictor import ModelPredictor
from backend.utils.model_checker import ModelChecker


def show():
    """Display AI Insights page"""
    
    st.markdown("# 🤖 AI Insights & Model Explanation")
    st.markdown("Machine Learning model performance and feature analysis")
    
    st.markdown("---")
    
    # Section 2: Our Model Configuration
    st.markdown("## ⚙️ Model Configuration")
    
    config_data = {
        'Parameter': [
            'Algorithm',
            'Number of Trees',
            'Max Depth',
            'Min Samples Split',
            'Min Samples Leaf',
            'Random State',
            'Training Data Split'
        ],
        'Value': [
            MODEL_CONFIG['model_type'],
            f"{MODEL_CONFIG['n_estimators']} trees",
            f"{MODEL_CONFIG['max_depth']} levels",
            f"{MODEL_CONFIG['min_samples_split']} samples",
            f"{MODEL_CONFIG['min_samples_leaf']} samples",
            f"{MODEL_CONFIG['random_state']} (for reproducibility)",
            f"{100 - int(MODEL_CONFIG['test_size']*100)}% train / {int(MODEL_CONFIG['test_size']*100)}% test"
        ],
        'Explanation': [
            'Machine Learning algorithm used',
            'Number of decision trees in forest',
            'Maximum depth of each tree',
            'Minimum samples to split a node',
            'Minimum samples in leaf node',
            'Ensures reproducible results',
            'Data split for training and validation'
        ]
    }
    
    config_df = pd.DataFrame(config_data)
    st.dataframe(config_df, width="stretch")
    
    st.markdown("---")
    
    # Section 3: Technical Features Used
    st.markdown("## 📊 Technical Indicators (Features)")
    
    st.markdown("""
    The model uses **10 technical indicators** as input features:
    """)
    
    features_explanation = {
        'Indicator': list(FEATURE_INFO.keys()),
        'Description': [
            feat_info.get('description', feat_info)
            if isinstance(feat_info, dict)
            else feat_info
            for feat_info in FEATURE_INFO.values()
        ],
        'Type': ['Trend', 'Trend', 'Momentum', 'Trend', 'Trend', 'Trend', 'Volatility', 'Volatility', 'Returns', 'Risk']
    }
    
    features_df = pd.DataFrame(features_explanation)
    st.dataframe(features_df, width="stretch")
    
    st.markdown("---")
    
    # Section 4: Feature Importance
    st.markdown("## 🎯 Feature Importance")
    
    if st.session_state.selected_company is not None:
        ticker = st.session_state.current_ticker
        company_name = st.session_state.selected_company
        
        model_checker = ModelChecker()
        
        if not model_checker.has_model(ticker):
            st.warning(f"❌ No model available for {company_name} ({st.session_state.selected_exchange})")
            st.info("Select a different company/exchange from Dashboard that has a trained model.")
        else:
            with st.spinner("Loading model metrics..."):
                try:
                    predictor = ModelPredictor(company_name, ticker)
                    
                    if predictor.load_model():
                        importance = predictor.get_feature_importance(top_n=10)
                        
                        if importance:
                            st.markdown(f"""
                            **Feature Importance for {company_name}**
                            
                            Shows which indicators are most important for predictions:
                            """)
                            
                            # Create dataframe for visualization
                            importance_df = pd.DataFrame([
                                {'Feature': feat, 'Importance': score}
                                for feat, score in importance.items()
                            ])
                            
                            # Create bar chart
                            import plotly.express as px
                            fig = px.bar(
                                importance_df,
                                x='Importance',
                                y='Feature',
                                orientation='h',
                                title='Feature Importance Score',
                                color='Importance',
                                color_continuous_scale='Viridis'
                            )
                            fig.update_layout(template='plotly_dark', height=400)
                            st.plotly_chart(fig, width="stretch")
                            
                            # Show importance values
                            st.dataframe(importance_df, width="stretch")
                except Exception as e:
                    st.error(f"Error loading feature importance: {str(e)}")
    else:
        st.info("Select a company in Dashboard to see feature importance")
    
    st.markdown("---")
    
    # Section 5: Model Evaluation Metrics
    st.markdown("## 📈 Model Performance Metrics")
    
    st.markdown("""
    The model is evaluated using three key metrics:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### MAE\nAverage prediction error")
    
    with col2:
        st.markdown("### RMSE\nRoot mean squared error")
    
    with col3:
        st.markdown("### R²\nVariance explained (0-1)")
    
    st.markdown("---")
    
    # Section 6: Our Model Results
    st.markdown("## 🏆 Our Model Results")
    
    if st.session_state.selected_company is not None:
        ticker = st.session_state.current_ticker
        company_name = st.session_state.selected_company
        
        model_checker = ModelChecker()
        
        if not model_checker.has_model(ticker):
            st.warning(f"❌ No model available for {company_name} ({st.session_state.selected_exchange})")
        else:
            with st.spinner("Loading model results..."):
                try:
                    predictor = ModelPredictor(company_name, ticker)
                    
                    if predictor.load_model():
                        metrics = predictor.get_model_metrics()
                        
                        if metrics:
                            st.markdown(f"**Metrics for {company_name} ({ticker})**")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Test MAE", metrics['Test MAE'])
                            
                            with col2:
                                st.metric("Test RMSE", metrics['Test RMSE'])
                            
                            with col3:
                                st.metric("Test R²", metrics['Test R²'])
                            
                            # Note: Train metrics intentionally hidden per user request
                            
                except Exception as e:
                    st.error(f"Error loading model results: {str(e)}")
    else:
        st.info("Select a company to see model metrics")
    
    st.markdown("---")
    
    st.markdown("---")
    
    st.warning("⚠️ Use predictions as guidance only. Always do your own research and consult financial advisors.")
    
    st.markdown("---")


if __name__ == "__main__":
    show()
