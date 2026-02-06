import pandas as pd
import random
import streamlit as st
from datetime import datetime

LOG_TEMPLATES = {
    "INFO": [
        "Health check passed for service 'payments-v2'",
        "Incoming request: GET /api/v1/user/1023",
        "Cache hit for key 'session:1023'",
        "Database connection pool: 5/20 utilized",
        "Routine maintenance task scheduled",
        "User login successful (IP: 192.168.1.10)"
    ],
    "WARNING": [
        "High memory usage detected (75%) in pod 'frontend-5b'",
        "Database query took longer than expected (350ms)",
        "Rate limit approaching for API key 'client_web'",
        "Disk usage on /var/log is at 80%",
        "Deprecation warning: method 'getUser' will be removed"
    ],
    "ERROR": [
        "Connection refused: mongodb://db-primary:27017",
        "Timeout waiting for upstream service 'inventory'",
        "NullPointerException in PaymentController.process()",
        "Transaction rolled back due to deadlock",
        "Critical input validation failure",
        "Segment fault in experimental module"
    ]
}

def generate_logs_for_row(row):
    """
    Generate logs based on the row's status and metrics.
    Returns a list of dicts.
    """
    logs = []
    
    # 1. Determine severity mix based on alert status
    if row['alert_status'] == 'ALERT':
        num_logs = random.randint(3, 8)
        # Heavy on Errors
        weights = {"INFO": 0.1, "WARNING": 0.3, "ERROR": 0.6}
        # Add a specific error related to the root cause if present
        if 'predicted_root_cause' in row:
            logs.append({
                "timestamp": row['timestamp'],
                "level": "ERROR",
                "message": f"Critical Failure: {row['predicted_root_cause']} detected. Immediate attention required."
            })
    else:
        num_logs = random.randint(1, 3)
        # Mostly Info
        weights = {"INFO": 0.9, "WARNING": 0.1, "ERROR": 0.0}

    # 2. detailed logic based on metrics
    if row['cpu_usage'] > 80:
        logs.append({
            "timestamp": row['timestamp'],
            "level": "WARNING",
            "message": f"CPU Throttling detected: Usage at {row['cpu_usage']}%"
        })
        
    if row['response_time'] > 1500:
        logs.append({
            "timestamp": row['timestamp'],
            "level": "ERROR",
            "message": f"Upstream Timeout: Request took {row['response_time']}ms"
        })

    # 3. Fill the rest with random templates
    choices = list(weights.keys())
    probs = list(weights.values())
    
    for _ in range(num_logs):
        level = random.choices(choices, weights=probs, k=1)[0]
        msg = random.choice(LOG_TEMPLATES[level])
        logs.append({
            "timestamp": row['timestamp'],
            "level": level,
            "message": msg
        })
        
    return logs

@st.cache_data(show_spinner=False)
def generate_log_dataframe(main_df):
    """
    Takes the main metrics DataFrame and expands it into a Log DataFrame
    """
    if main_df.empty:
        return pd.DataFrame(columns=["timestamp", "level", "message"])
        
    all_logs = []
    # Only generate logs for the viewed window (e.g. last 100 rows to be fast)
    # or generating for the whole view_df passed in
    
    for _, row in main_df.iterrows():
        row_logs = generate_logs_for_row(row)
        all_logs.extend(row_logs)
        
    log_df = pd.DataFrame(all_logs)
    if not log_df.empty:
        log_df = log_df.sort_values("timestamp")
        
    return log_df
