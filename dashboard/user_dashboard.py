"""
User Dashboard - Premium Glassmorphism Version (Refined)
"""
import os
import sys
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lazy imports - only import when needed to speed up initial load
# from backend.report_generator import generate_pdf_report
# from dashboard.utils.config_manager import load_config
# from dashboard.forecasting_engine import show_forecasting_page
# from dashboard.log_explorer import show_log_explorer_page

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AIOps Premium Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# MAIN APP FUNCTION
# -----------------------------
def main():
    # -----------------------------
    # PATHS
    # -----------------------------
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "final_decision_output.csv")

    # -----------------------------
    # GLASSMORPHISM CSS
    # -----------------------------
    st.markdown("""
    <style>
        /* FORCE DARK THEME ON SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            background-image: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Global App Background */
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgb(15, 23, 42) 0%, rgb(33, 40, 58) 90%);
            color: #e2e8f0;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6, label, p {
            color: #e2e8f0 !important;
            font-family: 'Inter', sans-serif;
        }

        /* Sidebar Input Labels */
        .stSelectbox label, .stSlider label {
            color: #f8fafc !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }

        /* Slider Min/Max Labels (Fixing visibility) */
        [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {
            color: #f8fafc !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }
        
        /* Input Boxes */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #334155 !important;
            color: white !important;
            border: 1px solid #475569 !important;
        }
        
        /* Status Text Class */
        .status-text {
            font-weight: 800;
            letter-spacing: 1px;
            margin-top: 0.8rem;
        }
        
        /* Glass Cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
        }
        
        /* KPI Values */
        .kpi-title {
            color: #94a3b8 !important;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: white !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Button Styling */
        .stButton > button {
            background-color: #3b82f6 !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------
    # UTIL: Load dataset
    # -----------------------------
    @st.cache_data(show_spinner=False)
    def load_data(path: str) -> pd.DataFrame:
        if not os.path.exists(path):
            return pd.DataFrame()
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        return df

    # -----------------------------
    # CHECK USER SESSION
    # -----------------------------
    if "user" not in st.session_state:
        st.error("🔒 Please login first")
        if st.button("Go to Login"):
            st.rerun()
        st.stop()
        
    current_user = st.session_state.user

    # -----------------------------
    # MAIN LAYOUT
    # -----------------------------
    # Show loading spinner while data loads
    with st.spinner("🔄 Loading dashboard data..."):
        df = load_data(DATA_FILE)
    
    if df.empty:
        st.error("❌ No data found.")
        st.stop()

    # Header
    col_header, col_profile = st.columns([6, 2])
    with col_header:
        st.markdown("# ⚡ AIOps Control Center")
        st.markdown(f"**{current_user['username']}** • {datetime.now().strftime('%B %d, %Y')}")

    with col_profile:
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("---")

    # -----------------------------
    # SIDEBAR NAVIGATION & FILTERS
    # -----------------------------
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.radio("Go to", ["📊 Monitoring Dashboard", "🤖 Command Center", "🔮 Predictive Forecasting", "📝 Log Intelligence"])
        
        st.markdown("---")
        st.markdown("### 🎛️ Controls")
        
        if st.button("📄 Generate Report", use_container_width=True):
            with st.spinner("Generating..."):
                from backend.report_generator import generate_pdf_report
                pdf_file = generate_pdf_report(df)
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_file,
                    file_name=f"aiops_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        st.markdown("---")
        if HAS_GENAI:
            st.markdown("### 🔑 AI Configuration")
            api_key_input = st.text_input("Gemini API Key", value="AIzaSyC6MI7Z9rG_8kTMgk12-1_FH6TlOLrqp6s", type="password")
        else:
            st.error("⚠️ Gemini Library Missing. Run: `pip install google-generativeai`")
        
        st.markdown("---")
        window = st.slider("Time Window", 50, 1500, 250)
        alert_filter = st.selectbox("Status Filter", ["ALL", "ALERT", "OK"])

    # -----------------------------
    # LOAD CONFIG (Lazy import)
    # -----------------------------
    from dashboard.utils.config_manager import load_config
    config = load_config()
    CPU_THRESH = config.get("cpu_threshold", 80)
    MEM_THRESH = config.get("memory_threshold", 8)
    LAT_THRESH = config.get("latency_threshold", 1000)

    # Filter Logic (Common)
    view_df = df.tail(window).copy()

    if alert_filter != "ALL":
        view_df = view_df[view_df["alert_status"] == alert_filter]

    if view_df.empty:
        st.warning(f"⚠️ No records found with status: {alert_filter}")
        st.stop()

    latest = view_df.iloc[-1]

    # -----------------------------
    # PAGE 1: MONITORING DASHBOARD
    # -----------------------------
    if page == "📊 Monitoring Dashboard":
        # KPI GRID
        st.markdown("### 📊 System Status")
        k1, k2, k3, k4 = st.columns(4)

        def kpi_card(title, value, unit, status="normal", icon=""):
            # Colors: Normal=Green, Critical=Yellow, Warning=Red
            if status == "normal":
                bg_color = "rgba(34, 197, 94, 0.2)"
                border_color = "#22c55e"
                text_color = "#4ade80"
            elif status == "critical":
                bg_color = "rgba(234, 179, 8, 0.2)"
                border_color = "#eab308"
                text_color = "#facc15"
            else: # warning/alert
                bg_color = "rgba(239, 68, 68, 0.2)"
                border_color = "#ef4444"
                text_color = "#f87171"
            
            return f"""
            <div class="glass-card">
                <div class="kpi-title">{icon} {title}</div>
                <div class="kpi-value">{value}<span style="font-size: 1.0rem; opacity: 0.7;"> {unit}</span></div>
                <div style="margin-top: 0.8rem;">
                    <span style="background-color: {bg_color}; border: 1px solid {border_color}; color: {text_color}; padding: 4px 12px; border-radius: 99px; font-weight: 700; font-size: 0.85rem; letter-spacing: 1px;">
                        ● {status.upper()}
                    </span>
                </div>
            </div>
            """

        with k1:
            cpu = latest['cpu_usage']
            state = "critical" if cpu > CPU_THRESH else "warning" if cpu > (CPU_THRESH * 0.75) else "normal"
            st.markdown(kpi_card("CPU Load", f"{cpu:.1f}", "%", state, "💻"), unsafe_allow_html=True)

        with k2:
            mem = latest['memory_usage']
            state = "critical" if mem > MEM_THRESH else "warning" if mem > (MEM_THRESH * 0.75) else "normal"
            st.markdown(kpi_card("Memory", f"{mem:.1f}", "GB", state, "🧠"), unsafe_allow_html=True)

        with k3:
            resp = latest['response_time']
            state = "critical" if resp > LAT_THRESH else "warning" if resp > (LAT_THRESH * 0.5) else "normal"
            st.markdown(kpi_card("Latency", f"{resp:.0f}", "ms", state, "⚡"), unsafe_allow_html=True)

        with k4:
            anom = latest.get('anomaly_label', 0)
            state = "critical" if anom == 1 else "normal"
            val = "DETECTED" if anom == 1 else "NONE"
            st.markdown(kpi_card("Anomaly", val, "", state, "🛡️"), unsafe_allow_html=True)

        # ANALYSIS TABS
        st.markdown("### 📈 Deep Dive & Graphs")
        tab1, tab2, tab3 = st.tabs(["💻 CPU Incidents", "🧠 Memory Incidents", "⚡ Latency Incidents"])

        def hex_to_rgba(h, alpha=0.1):
            h = h.lstrip('#')
            return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alpha})"

        def create_incident_chart(df, metric, title, threshold, color):
            fig = go.Figure()
            
            # 1. Main Line
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df[metric],
                mode='lines', name=title,
                line=dict(width=2, color=color),
                fill='tozeroy', fillcolor=hex_to_rgba(color, 0.1)
            ))
            
            # 2. Alert Markers
            alerts = df[df['alert_status'] == 'ALERT']
            if not alerts.empty:
                fig.add_trace(go.Scatter(
                    x=alerts['timestamp'], y=alerts[metric],
                    mode='markers', name='Failure Event',
                    marker=dict(symbol='x', size=10, color='red', line=dict(width=2, color='white'))
                ))
            
            # 3. Threshold Line
            fig.add_hline(y=threshold, line_dash="dash", line_color="orange", annotation_text=f"Limit ({threshold})")
            
            fig.update_layout(
                title=f"{title} - Incident Analysis",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1'), height=400,
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            return fig

        with tab1:
            st.plotly_chart(create_incident_chart(view_df, 'cpu_usage', 'CPU Load', CPU_THRESH, '#3b82f6'), use_container_width=True)

        with tab2:
            st.plotly_chart(create_incident_chart(view_df, 'memory_usage', 'Memory Usage', MEM_THRESH, '#a855f7'), use_container_width=True)

        with tab3:
            st.plotly_chart(create_incident_chart(view_df, 'response_time', 'Latency', LAT_THRESH, '#06b6d4'), use_container_width=True)

        # SECOND ROW: DISTRIBUTION
        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("##### 🔍 Root Cause Breakdown")
            rc_counts = view_df['predicted_root_cause'].value_counts()
            fig_pie = go.Figure(data=[go.Pie(
                labels=rc_counts.index, 
                values=rc_counts.values,
                hole=.5,
                marker=dict(colors=['#3b82f6', '#10b981', '#ef4444']),
                textinfo='label+percent'
            )])
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'), height=300, margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.markdown("##### 🛡️ Alert Status Distribution")
            alert_counts = view_df['alert_status'].value_counts()
            fig_alert = go.Figure(data=[go.Pie(
                labels=alert_counts.index, 
                values=alert_counts.values,
                hole=.5,
                marker=dict(colors=['#ef4444', '#10b981']),
                textinfo='label+percent'
            )])
            fig_alert.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'), height=300, margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig_alert, use_container_width=True)

    # -----------------------------
    # PAGE 2: COMMAND CENTER
    # -----------------------------
    elif page == "🤖 Command Center":
        # COMMAND CENTER (Phase 7.3)
        st.markdown("### 🤖 AIOps Command Center")

        # Create Columns for Command Center Layout
        cc1, cc2 = st.columns([1.5, 1])

        with cc1:
            # Chat Interface
            st.markdown("##### 💬 AIOps Assistant (Gemini Pro)")
            
            # Initialize Chat History
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": "Hello! I am connected to **Google Gemini Pro**. Click '✨ Analyze System' for a deep dive, or ask me anything about the system status!"}
                ]

            # Display Chat History
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat Logic
            prompt = st.chat_input("Ask Gemini about system health...")
            
            # Button for Auto-Analysis
            if st.button("✨ Analyze System with Gemini Pro", use_container_width=True):
                prompt = f"""
                You are a Senior Site Reliability Engineer (SRE). Analyze the following system metrics:
                - CPU Usage: {latest['cpu_usage']:.1f}%
                - Memory Usage: {latest['memory_usage']:.1f} GB
                - Latency: {latest['response_time']:.0f} ms
                - Anomaly Detected: {'YES' if latest.get('anomaly_label', 0)==1 else 'NO'}
                
                Task:
                1. Diagnose the system health.
                2. If there are issues, explain the potential root cause.
                3. Suggest 3 specific remediation steps.
                4. Be concise and professional.
                """

            if prompt:
                # User Message
                if not prompt.startswith("You are a Senior"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                else:
                    # It's a system prompt from the button, don't show the raw prompt to user, just show "Analyzing..."
                    with st.chat_message("user"):
                        st.markdown("**Requesting System Analysis...**")
                    st.session_state.messages.append({"role": "user", "content": "**System Analysis Request**"})

                # Gemini Response Logic
                if HAS_GENAI:
                    try:
                        genai.configure(api_key=api_key_input)
                        # Using gemini-2.0-flash as confirmed by user's available model list
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        
                        with st.spinner("Gemini (2.0 Flash) is analyzing system metrics..."):
                            response = model.generate_content(prompt)
                            bot_reply = response.text
                        
                        # Assistant Message
                        with st.chat_message("assistant"):
                            st.markdown(bot_reply)
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                        
                    except Exception as e:
                        error_msg = f"❌ **API Error**: {str(e)}. Please check your API Key."
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    error_msg = "❌ **Dependency Error**: `google-generativeai` not installed. Please try: `pip install google-generativeai`"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
        with cc2:
            st.markdown("#### 🛠️ Remediation Actions")
            # Action Grid
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("♻️ Restart Service", use_container_width=True):
                    st.toast("Initiating safe restart sequence...", icon="⏳")
                    time.sleep(1)
                    st.toast("Service 'payments-v2' restarted successfully!", icon="✅")
                    
                if st.button("⚖️ Scale Up Pods", use_container_width=True):
                    st.toast("Scaling request sent to Kubernetes Cluster.", icon="🚀")
                    
            with ac2:
                if st.button("🧹 Clear DB Cache", use_container_width=True):
                    st.toast("Redis Cache flushed.", icon="🧹")
                    
                if st.button("📢 Page SRE Team", use_container_width=True):
                    st.toast("Alert sent to #ops-critical slack channel.", icon="🔔")

            # Feedback Loop (Only visible if something is wrong)
            if latest.get('anomaly_label', 0) == 1 or latest['cpu_usage'] > CPU_THRESH:
                st.markdown("---")
                st.markdown("**🛡️ Model Feedback**")
                fb1, fb2 = st.columns(2)
                if fb1.button("✅ Confirm Issue", use_container_width=True):
                    st.success("Thanks! Labeled as True Positive.")
                if fb2.button("❌ False Alarm", use_container_width=True):
                    st.error("Marked as False Positive. Retraining scheduled.")

    # -----------------------------
    # PAGE 3: PREDICTIVE FORECASTING
    # -----------------------------
    elif page == "🔮 Predictive Forecasting":
        from dashboard.forecasting_engine import show_forecasting_page
        show_forecasting_page(view_df)

    # -----------------------------
    # PAGE 4: LOG INTELLIGENCE
    # -----------------------------
    elif page == "📝 Log Intelligence":
        from dashboard.log_explorer import show_log_explorer_page
        show_log_explorer_page(view_df)

if __name__ == "__main__":
    main()
