import streamlit as st
import pandas as pd
from dashboard.utils.log_generator import generate_log_dataframe

def show_log_explorer_page(df):
    st.markdown("### 📝 Log Intelligence Explorer")
    st.markdown("Deep dive into system logs correlated with metric anomalies.")
    
    if df.empty:
        st.warning("No data available to generate logs.")
        return

    # Generate logs on the fly based on current view of metrics
    # In a real app, this would query Elasticsearch/Splunk
    with st.spinner("Indexing logs from active session..."):
        log_df = generate_log_dataframe(df)

    # -----------------------------
    # FILTERS
    # -----------------------------
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search Logs (Regex supported)", placeholder="e.g. 'Timeout' or 'Error 500'")
    with col2:
        level_filter = st.multiselect("Severity", ["INFO", "WARNING", "ERROR"], default=["WARNING", "ERROR"])

    # -----------------------------
    # FILTER LOGIC
    # -----------------------------
    filtered_logs = log_df.copy()
    
    # Severity Filter
    if level_filter:
        filtered_logs = filtered_logs[filtered_logs['level'].isin(level_filter)]
        
    # Search Filter
    if search_term:
        filtered_logs = filtered_logs[
            filtered_logs['message'].str.contains(search_term, case=False, na=False)
        ]

    # -----------------------------
    # DISPLAY
    # -----------------------------
    st.markdown(f"**Found {len(filtered_logs)} logs**")
    
    # Custom styling for logs
    def color_log_level(val):
        color = 'white'
        if val == 'ERROR': color = '#ef4444'
        elif val == 'WARNING': color = '#eab308'
        elif val == 'INFO': color = '#3b82f6'
        return f'color: {color}; font-weight: bold'

    if not filtered_logs.empty:
        # Show as a styled table or raw text
        # Using Streamlit dataframe with column config
        st.dataframe(
            filtered_logs, 
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Timestamp", format="D MMM, HH:mm:ss"),
                "level": "Severity",
                "message": "Log Message"
            },
            hide_index=True
        )
    else:
        st.info("No logs match your filter criteria.")
