import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
import streamlit as st
from datetime import timedelta

@st.cache_data(show_spinner=False)
def forecast_metric(df, metric_name, periods=30):
    """
    Forecast a metric for the next 'periods' time steps.
    Returns: dates (future), predicted_values
    """
    # Prepare data for training
    # Use simple integer index as feature for time
    df = df.dropna(subset=[metric_name]).copy()
    if len(df) < 10:
        return None, None
        
    df['time_idx'] = np.arange(len(df))
    
    X = df[['time_idx']].values
    y = df[metric_name].values
    
    # Train simple model (RandomForest is better for capturing non-linear patterns)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Create future features
    last_idx = df['time_idx'].iloc[-1]
    future_X = np.arange(last_idx + 1, last_idx + 1 + periods).reshape(-1, 1)
    
    # Predict
    predictions = model.predict(future_X)
    
    # Generate future timestamps
    last_date = df['timestamp'].iloc[-1]
    # Assuming avg time difference between points
    avg_diff = df['timestamp'].diff().mean()
    if pd.isna(avg_diff):
        avg_diff = timedelta(seconds=60)
        
    future_dates = [last_date + (avg_diff * i) for i in range(1, periods + 1)]
    
    return future_dates, predictions

def show_forecasting_page(df):
    """
    Render the forecasting page in Streamlit
    """
    st.markdown("### 🔮 Predictive Forecasting")
    st.markdown("AI-driven predictions for system metrics over the next hour.")
    
    if df.empty:
        st.error("Not enough data to generate forecast.")
        return

    # User controls
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox("Select Metric to Forecast", ["CPU Usage", "Memory Usage", "Response Time"])
        metric_map = {
            "CPU Usage": "cpu_usage", 
            "Memory Usage": "memory_usage", 
            "Response Time": "response_time"
        }
        selected_col = metric_map[metric]
        
    with col2:
        horizon = st.slider("Forecast Horizon (Steps)", 10, 100, 30)
        
    # Generate Forecast
    with st.spinner(f"Training model on {len(df)} data points..."):
        future_dates, predictions = forecast_metric(df, selected_col, periods=horizon)
        
    if future_dates is None:
        st.warning("Insufficient data training.")
        return

    # Color mapping from user_dashboard.py
    color_map = {
        "CPU Usage": "#3b82f6",      # Blue
        "Memory Usage": "#a855f7",   # Purple
        "Response Time": "#06b6d4"   # Cyan
    }
    chart_color = color_map.get(metric, "#3b82f6")

    # Plotting
    fig = go.Figure()
    
    # Historical Data (Last 100 points for context)
    history_df = df.tail(100)
    fig.add_trace(go.Scatter(
        x=history_df['timestamp'],
        y=history_df[selected_col],
        mode='lines',
        name='Historical (Actual)',
        line=dict(color=chart_color, width=2),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(int(chart_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}"
    ))
    
    # Forecast Data
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        mode='lines',
        name='AI Forecast',
        line=dict(color=chart_color, width=2, dash='dot')
    ))
    
    fig.update_layout(
        title=f"{metric} Forecast",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1'),
        height=500,
        xaxis_title="Time",
        yaxis_title=metric
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    avg_predicted = np.mean(predictions)
    max_predicted = np.max(predictions)
    
    st.markdown("#### 🧠 AI Insights")
    i1, i2 = st.columns(2)
    with i1:
        st.info(f"**Average Predicted Value:** {avg_predicted:.2f}")
    with i2:
        if metric == "CPU Usage" and max_predicted > 85:
            st.error(f"⚠️ **Warning:** Forecast predicts CPU spike to {max_predicted:.1f}%!")
        elif metric == "Memory Usage" and max_predicted > 7.5:
            st.warning(f"⚠️ **Caution:** Memory trending high ({max_predicted:.1f} GB).")
        else:
            st.success("✅ **Stable:** No critical spikes predicted.")
