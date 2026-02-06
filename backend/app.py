"""
AIOps Dashboard Backend API
Flask REST API for serving dashboard data (CSV-based)
MongoDB used ONLY for login tracking
"""
import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.login_tracker import get_login_tracker

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "final_decision_output.csv")

# -----------------------------
# SIMPLE LOGIN DATABASE (in-memory)
# -----------------------------
USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "user": {"password": "user123", "role": "USER"}
}

# -----------------------------
# INITIALIZE LOGIN TRACKER
# -----------------------------
login_tracker = get_login_tracker()

# -----------------------------
# UTIL: Load dataset
# -----------------------------
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df

# Load data once at startup
try:
    df = load_data(DATA_FILE)
    print(f"[OK] Loaded {len(df)} records from CSV")
except Exception as e:
    print(f"[ERROR] Failed to load data: {e}")
    df = pd.DataFrame()

# -----------------------------
# API ROUTES
# -----------------------------

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "records": len(df),
        "mongodb_connected": login_tracker.db is not None
    })

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint with MongoDB tracking"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Get client info for tracking
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    user = USERS.get(username)
    if user and user["password"] == password:
        # Log successful login to MongoDB
        login_tracker.log_login(
            username=username,
            role=user["role"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return jsonify({
            "success": True,
            "username": username,
            "role": user["role"]
        })
    else:
        # Log failed login attempt
        if username:
            login_tracker.log_failed_login(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

@app.route('/api/ingest', methods=['POST'])
def ingest_data():
    """Ingest new metrics data (Real-time stream)"""
    global df
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Validations
        required = ['cpu_usage', 'memory_usage', 'response_time']
        if not all(k in data for k in required):
            return jsonify({"success": False, "error": f"Missing required fields: {required}"}), 400
        
        # Validate data types
        try:
            data['cpu_usage'] = float(data['cpu_usage'])
            data['memory_usage'] = float(data['memory_usage'])
            data['response_time'] = float(data['response_time'])
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid data types for metrics"}), 400
            
        # Add timestamp if missing
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        
        # Determine Status (Simple Rule for Demo)
        data['alert_status'] = "ALERT" if data['cpu_usage'] > 80 or data['response_time'] > 1000 else "OK"
        data['predicted_root_cause'] = "CPU_OVERLOAD" if data['cpu_usage'] > 80 else "LATENCY_SPIKE" if data['response_time'] > 1000 else "NORMAL"
        data['recommended_action'] = "Check Logs" if data['alert_status'] == "ALERT" else "No action needed"
        data['failure_probability'] = 0.8 if data['alert_status'] == "ALERT" else 0.1
        data['anomaly_label'] = 1 if data['alert_status'] == "ALERT" else 0
        data['anomaly_score'] = abs(data['cpu_usage'] - 50) / 100.0  # Simple anomaly score
        data['error_count'] = data.get('error_count', 0)
        data['predicted_failure'] = 1 if data['failure_probability'] > 0.5 else 0
        
        # Append to DataFrame
        new_row = pd.DataFrame([data])
        new_row['timestamp'] = pd.to_datetime(new_row['timestamp'], errors='coerce')
        
        # Handle empty dataframe case
        if df.empty:
            df = new_row.copy()
        else:
            df = pd.concat([df, new_row], ignore_index=True)
        
        # Optional: Save back to CSV occasionally (skipping for performance demo)
        
        return jsonify({
            "success": True, 
            "message": "Data ingested successfully", 
            "total_records": len(df),
            "ingested_record": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get filtered data based on query parameters"""
    try:
        # Check if dataframe is empty
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No data available. Please ensure CSV file exists and contains data."
            }), 404
        
        # Get query parameters
        alert_filter = request.args.get('alert_status', 'ALL')
        root_filter = request.args.get('root_cause', 'ALL')
        window = int(request.args.get('window', 250))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Apply filters
        filtered = df.copy()
        
        if alert_filter != "ALL":
            filtered = filtered[filtered["alert_status"] == alert_filter]
        
        if root_filter != "ALL":
            filtered = filtered[filtered["predicted_root_cause"] == root_filter]
        
        # Date range filter
        if start_date and end_date:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            filtered = filtered[
                (filtered["timestamp"] >= start) &
                (filtered["timestamp"] <= end)
            ]
        
        # Check if filtered result is empty
        if filtered.empty:
            return jsonify({
                "success": False,
                "error": "No data found for selected filters"
            }), 404
        
        # Apply window
        view_df = filtered.tail(window).copy()
        
        # Check if view_df is empty after window
        if view_df.empty:
            return jsonify({
                "success": False,
                "error": "No data in selected window"
            }), 404
        
        # Get latest record
        latest = view_df.iloc[-1].to_dict()
        
        # Convert timestamp to string for JSON
        latest['timestamp'] = str(latest['timestamp'])
        
        # Calculate statistics
        alerts_count = int((view_df["alert_status"] == "ALERT").sum())
        ok_count = int((view_df["alert_status"] == "OK").sum())
        anom_count = int((view_df.get("anomaly_label", 0) == 1).sum()) if "anomaly_label" in view_df.columns else 0
        
        root_causes = view_df["predicted_root_cause"].value_counts().to_dict()
        
        return jsonify({
            "success": True,
            "data": view_df.to_dict('records'),
            "latest": latest,
            "statistics": {
                "total_records": len(view_df),
                "alerts_count": alerts_count,
                "ok_count": ok_count,
                "anomalies_count": anom_count,
                "root_causes": root_causes
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/kpi', methods=['GET'])
def get_kpi():
    """Get KPI metrics"""
    try:
        # Check if dataframe is empty
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No data available"
            }), 404
        
        window = int(request.args.get('window', 250))
        view_df = df.tail(window).copy()
        
        # Check if view_df is empty
        if view_df.empty:
            return jsonify({
                "success": False,
                "error": "No data in selected window"
            }), 404
        
        latest = view_df.iloc[-1]
        
        return jsonify({
            "success": True,
            "kpi": {
                "cpu_usage": float(latest['cpu_usage']),
                "memory_usage": float(latest['memory_usage']),
                "response_time": float(latest['response_time']),
                "failure_probability": float(latest['failure_probability']),
                "anomaly_label": int(latest.get("anomaly_label", 0)),
                "alert_status": str(latest["alert_status"]),
                "timestamp": str(latest['timestamp'])
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        # Check if dataframe is empty
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No data available"
            }), 404
        
        window = int(request.args.get('window', 250))
        view_df = df.tail(window).copy()
        
        # Check if view_df is empty
        if view_df.empty:
            return jsonify({
                "success": False,
                "error": "No data in selected window"
            }), 404
        
        # Root cause distribution
        rc_counts = view_df["predicted_root_cause"].value_counts().to_dict() if "predicted_root_cause" in view_df.columns else {}
        
        # Alert status distribution
        alert_counts = view_df["alert_status"].value_counts().to_dict() if "alert_status" in view_df.columns else {}
        
        # Correlation matrix
        metrics = ['cpu_usage', 'memory_usage', 'response_time', 'failure_probability']
        available_metrics = [m for m in metrics if m in view_df.columns]
        
        if len(available_metrics) > 1:
            corr_matrix = view_df[available_metrics].corr().to_dict()
            stats = view_df[available_metrics].describe().to_dict()
        else:
            corr_matrix = {}
            stats = {}
        
        return jsonify({
            "success": True,
            "root_causes": rc_counts,
            "alert_status": alert_counts,
            "correlation": corr_matrix,
            "statistics": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get AI-powered insights"""
    try:
        # Check if dataframe is empty
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No data available"
            }), 404
        
        window = int(request.args.get('window', 250))
        view_df = df.tail(window).copy()
        
        # Check if view_df is empty
        if view_df.empty:
            return jsonify({
                "success": False,
                "error": "No data in selected window"
            }), 404
        
        total_records = len(view_df)
        alerts_count = int((view_df["alert_status"] == "ALERT").sum()) if "alert_status" in view_df.columns else 0
        anom_count = int((view_df.get("anomaly_label", 0) == 1).sum()) if "anomaly_label" in view_df.columns else 0
        
        alert_rate = (alerts_count / total_records * 100) if total_records > 0 else 0
        anomaly_rate = (anom_count / total_records * 100) if total_records > 0 else 0
        
        avg_cpu = float(view_df['cpu_usage'].mean()) if 'cpu_usage' in view_df.columns else 0.0
        avg_memory = float(view_df['memory_usage'].mean()) if 'memory_usage' in view_df.columns else 0.0
        avg_response = float(view_df['response_time'].mean()) if 'response_time' in view_df.columns else 0.0
        avg_failure_prob = float(view_df['failure_probability'].mean()) if 'failure_probability' in view_df.columns else 0.0
        
        # Hourly trends
        hourly_trends = []
        if 'timestamp' in view_df.columns and not view_df.empty:
            view_df['hour'] = view_df['timestamp'].dt.hour
            hourly_stats = view_df.groupby('hour').agg({
                'cpu_usage': 'mean' if 'cpu_usage' in view_df.columns else 'count',
                'memory_usage': 'mean' if 'memory_usage' in view_df.columns else 'count',
                'response_time': 'mean' if 'response_time' in view_df.columns else 'count',
                'alert_status': lambda x: (x == 'ALERT').sum() if 'alert_status' in view_df.columns else 0
            }).reset_index()
            hourly_trends = hourly_stats.to_dict('records')
        
        return jsonify({
            "success": True,
            "insights": {
                "alert_rate": alert_rate,
                "anomaly_rate": anomaly_rate,
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory,
                "avg_response": avg_response,
                "avg_failure_prob": avg_failure_prob,
                "hourly_trends": hourly_trends
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/options', methods=['GET'])
def get_options():
    """Get filter options"""
    try:
        # Check if dataframe is empty
        if df.empty:
            return jsonify({
                "success": True,
                "root_causes": [],
                "date_range": {
                    "min": "",
                    "max": ""
                }
            })
        
        alert_filter = request.args.get('alert_status', 'ALL')
        
        temp = df.copy()
        if alert_filter != "ALL" and "alert_status" in temp.columns:
            temp = temp[temp["alert_status"] == alert_filter]
        
        root_causes = []
        if "predicted_root_cause" in temp.columns:
            root_causes = sorted(temp["predicted_root_cause"].astype(str).unique().tolist())
        
        date_min = ""
        date_max = ""
        if "timestamp" in df.columns and not df.empty:
            date_min = str(df["timestamp"].min().date())
            date_max = str(df["timestamp"].max().date())
        
        return jsonify({
            "success": True,
            "root_causes": root_causes,
            "date_range": {
                "min": date_min,
                "max": date_max
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/login-history', methods=['GET'])
def get_login_history():
    """Get login history (Admin only) - MongoDB tracking"""
    try:
        limit = int(request.args.get('limit', 20))
        logins = login_tracker.get_recent_logins(limit=limit)
        
        return jsonify({
            "success": True,
            "logins": logins,
            "total": len(logins)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/login-stats', methods=['GET'])
def get_login_stats():
    """Get login statistics (Admin only) - MongoDB tracking"""
    try:
        stats = login_tracker.get_login_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting AIOps Backend API Server...")
    print(f"📊 Data file: {DATA_FILE}")
    print(f"📈 Records loaded: {len(df)}")
    print(f"🔐 MongoDB login tracking: {'Enabled' if login_tracker.db else 'Disabled'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
