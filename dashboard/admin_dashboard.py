"""
Admin Dashboard - Streamlit Version (CSV-based)
Admin-only dashboard reading from CSV files
"""
import os
import sys
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.utils.config_manager import load_config, save_config

# -----------------------------
# MAIN APP FUNCTION
# -----------------------------
def main():
    # -----------------------------
    # PAGE CONFIG (Must be first Streamlit command)
    # -----------------------------
    # Note: set_page_config should be called only once. 
    # If app.py calls it, we shouldn't call it here.
    # However, if running standalone, we need it.
    # We'll use a try-except block or check if it's already set (streamit doesn't expose easily).
    # Since app.py is the entry point, we can omit it here, OR rely on app.py's config.
    # But usually app.py sets title to "AIOps Dashboard". Admin might want specific title.
    # Streamlit raises error if set twice.
    # We will comment it out if imported, but that's hard to detect reliably.
    # Best practice: Only entry point sets config.
    pass

    # -----------------------------
    # PATHS
    # -----------------------------
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "final_decision_output.csv")

    # -----------------------------
    # CSS STYLING
    # -----------------------------
    st.markdown("""
    <style>
        .admin-header {
            background: linear-gradient(135deg, #d62728 0%, #ff6b6b 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .admin-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
        }
        
        .admin-card {
            background: linear-gradient(135deg, #262730 0%, #3a3d4a 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------
    # UTIL: Load dataset
    # -----------------------------
    @st.cache_data(show_spinner=False)
    def load_data(path: str) -> pd.DataFrame:
        """Load CSV data"""
        if not os.path.exists(path):
            return pd.DataFrame()
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        return df

    # -----------------------------
    # CHECK ADMIN ROLE
    # -----------------------------
    if "user" not in st.session_state or st.session_state.user.get("role") != "ADMIN":
        st.error("🔒 Access Denied: Admin privileges required")
        st.info("Please login as admin to access this page")
        if st.button("Go to Login"):
            st.rerun()
        st.stop()

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    if not os.path.exists(DATA_FILE):
        st.error(f"❌ Data file not found: {DATA_FILE}")
        st.info("💡 Please ensure final_decision_output.csv exists in data/processed/")
        st.stop()

    # Show loading spinner while data loads
    with st.spinner("🔄 Loading dashboard data..."):
        df = load_data(DATA_FILE)

    # -----------------------------
    # HEADER
    # -----------------------------
    st.markdown("""
    <div class="admin-header">
        <h1>👨‍💼 Admin Dashboard</h1>
        <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">
            System Administration • Advanced Analytics • Data Management
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_logout, col_user, col_space = st.columns([1, 2, 7])
    with col_logout:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col_user:
        st.markdown(f"""
        <div style="text-align: right; padding: 0.5rem;">
            <span style="color: #d62728; font-weight: 600;">👤 {st.session_state.user['username']}</span>
            <span style="color: #b0b0b0;">(ADMIN)</span>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------
    # TABS
    # -----------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 System Overview", 
        "📈 Advanced Analytics",
        "🔍 Data Management",
        "⚙️ Settings",
        "🔔 Alert Settings"
    ])

    # -----------------------------
    # TAB 1: System Overview
    # -----------------------------
    with tab1:
        st.markdown("### 📊 System Overview")
        
        # System Statistics
        total_records = len(df)
        alerts_count = int((df["alert_status"] == "ALERT").sum())
        ok_count = int((df["alert_status"] == "OK").sum())
        anom_count = int((df.get("anomaly_label", 0) == 1).sum()) if "anomaly_label" in df.columns else 0
        avg_failure_prob = df['failure_probability'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", total_records)
        with col2:
            st.metric("Active Alerts", alerts_count, delta=f"{ok_count} OK")
        with col3:
            st.metric("Anomalies Detected", anom_count)
        with col4:
            st.metric("Avg Failure Probability", f"{avg_failure_prob:.2%}")
        
        # Latest Incidents
        st.markdown("---")
        st.markdown("### 🚨 Latest Incidents")
        
        if df.empty:
            st.warning("No data available to display.")
        else:
            latest_incidents = df.tail(10)
            display_cols = ['timestamp', 'alert_status', 'predicted_root_cause', 
                           'cpu_usage', 'memory_usage', 'response_time', 'failure_probability']
            available_cols = [col for col in display_cols if col in latest_incidents.columns]
            st.dataframe(latest_incidents[available_cols], use_container_width=True)

    # -----------------------------
    # TAB 2: Advanced Analytics
    # -----------------------------
    with tab2:
        st.markdown("### 📈 Advanced Analytics")
        
        # Date range filter
        if df.empty:
            st.warning("No data available for analytics.")
            filtered_df = pd.DataFrame()
        else:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=df["timestamp"].min().date())
            with col2:
                end_date = st.date_input("End Date", value=df["timestamp"].max().date())
            
            # Filter data by date range
            filtered_df = df[
                (df["timestamp"].dt.date >= start_date) &
                (df["timestamp"].dt.date <= end_date)
            ]
        
        # Root Cause Distribution
        st.markdown("#### Root Cause Distribution")
        if filtered_df.empty or "predicted_root_cause" not in filtered_df.columns:
            st.info("No data available for root cause distribution.")
        else:
            rc_dist = filtered_df["predicted_root_cause"].value_counts()
            if len(rc_dist) > 0:
                fig = go.Figure(data=[
                    go.Bar(
                        x=rc_dist.index.astype(str),
                        y=rc_dist.values,
                        marker_color='#d62728',
                        text=rc_dist.values,
                        textposition='auto',
                        hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
                    )
                ])
                fig.update_layout(
                    title="Root Cause Distribution",
                    xaxis_title="Root Cause",
                    yaxis_title="Count",
                    template='plotly_dark',
                    height=400,
                    xaxis=dict(tickangle=-45)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for selected date range")
        
        # Statistics
        if len(filtered_df) > 0:
            st.markdown("#### Statistical Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg CPU", f"{filtered_df['cpu_usage'].mean():.1f}%")
            with col2:
                st.metric("Avg Memory", f"{filtered_df['memory_usage'].mean():.2f} GB")
            with col3:
                st.metric("Avg Response", f"{filtered_df['response_time'].mean():.0f} ms")
            with col4:
                st.metric("Avg Failure Prob", f"{filtered_df['failure_probability'].mean():.2%}")

    # -----------------------------
    # TAB 3: Data Management
    # -----------------------------
    with tab3:
        st.markdown("### 🔍 Data Management")
        
        st.info(f"📄 CSV file location: `{DATA_FILE}`")
        
        # Data file info
        if os.path.exists(DATA_FILE):
            st.success("✅ CSV file found")
            
            # Get file info
            file_size = os.path.getsize(DATA_FILE) / (1024 * 1024)  # MB
            st.info(f"📊 File size: **{file_size:.2f} MB**")
            st.info(f"📈 Total records: **{len(df)}**")
            
            # Show date range
            if 'timestamp' in df.columns:
                min_date = df['timestamp'].min()
                max_date = df['timestamp'].max()
                st.info(f"📅 Date range: **{min_date.date()}** to **{max_date.date()}**")
            
            # Show data preview
            st.markdown("---")
            st.markdown("#### 📋 Data Preview (First 10 rows)")
            display_cols = ['timestamp', 'cpu_usage', 'memory_usage', 'response_time', 
                          'alert_status', 'predicted_root_cause', 'failure_probability']
            available_cols = [col for col in display_cols if col in df.columns]
            st.dataframe(df[available_cols].head(10), use_container_width=True)
            
            # Download button
            st.markdown("---")
            st.markdown("#### 📥 Export Data")
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Full Dataset (CSV)",
                data=csv_data,
                file_name=f"aiops_data_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error(f"⚠️ CSV file not found at: `{DATA_FILE}`")
            st.info("Please ensure the data file exists in the correct location.")

    # -----------------------------
    # TAB 4: Settings
    # -----------------------------
    with tab4:
        st.markdown("### ⚙️ System Settings")
        
        st.markdown("#### 📊 Data Source Information")
        st.json({
            "Data File": DATA_FILE,
            "File Exists": os.path.exists(DATA_FILE),
            "Total Records": len(df) if os.path.exists(DATA_FILE) else 0,
            "Date Range": {
                "Start": str(df["timestamp"].min().date()) if os.path.exists(DATA_FILE) and 'timestamp' in df.columns else "N/A",
                "End": str(df["timestamp"].max().date()) if os.path.exists(DATA_FILE) and 'timestamp' in df.columns else "N/A"
            },
            "Columns": list(df.columns) if os.path.exists(DATA_FILE) else []
        })
        
        st.markdown("---")
        st.markdown("#### 🔄 Cache Management")
        if st.button("🔄 Clear Cache & Reload Data"):
            st.cache_data.clear()
            st.success("✅ Cache cleared! Data will be reloaded on next access.")
            st.rerun()

    # -----------------------------
    # TAB 5: Alert Settings
    # -----------------------------
    with tab5:
        st.markdown("### 🔔 Dynamic Alert Configuration")
        st.markdown("Adjust the thresholds that trigger alerts in the User Dashboard.")

        # Load current config
        current_config = load_config()

        with st.form("alert_config_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 💻 CPU")
                new_cpu = st.slider("CPU Alert Threshold (%)", 0, 100, current_config.get("cpu_threshold", 80))
                st.caption("Alert when CPU usage exceeds this value.")
                
            with col2:
                st.markdown("#### 🧠 Memory")
                new_mem = st.slider("Memory Alert Threshold (GB)", 0, 16, current_config.get("memory_threshold", 8))
                st.caption("Alert when Memory usage exceeds this value.")
                
            with col3:
                st.markdown("#### ⚡ Latency")
                new_latency = st.slider("Latency Alert Threshold (ms)", 0, 5000, current_config.get("latency_threshold", 1000), step=100)
                st.caption("Alert when Response Time exceeds this value.")
                
            st.markdown("---")
            submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
            
            if submitted:
                new_config = {
                    "cpu_threshold": new_cpu,
                    "memory_threshold": new_mem,
                    "latency_threshold": new_latency
                }
                if save_config(new_config):
                    st.success("✅ Settings saved successfully! User Dashboard will update immediately.")
                    st.balloons()
                else:
                    st.error("❌ Failed to save settings.")

if __name__ == "__main__":
    main()
