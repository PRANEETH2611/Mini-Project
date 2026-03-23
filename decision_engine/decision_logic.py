import os
import pandas as pd
import joblib
import sys

# Make package imports work when run as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.resolution_model import recommend_resolution

# -------------------------------
# PATH SETUP
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "metrics_features.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "final_decision_output.csv")

ANOMALY_MODEL_FILE = os.path.join(BASE_DIR, "models", "isolation_forest.pkl")
PRED_MODEL_FILE = os.path.join(BASE_DIR, "models", "incident_prediction_model.pkl")
ROOT_MODEL_FILE = os.path.join(BASE_DIR, "models", "root_cause_model.pkl")

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(DATA_FILE)
print("✅ Loaded metrics features dataset:", df.shape)

# -------------------------------
# FEATURE LIST
# -------------------------------
feature_cols = [
    "cpu_usage", "memory_usage", "response_time", "error_count",
    "cpu_ma", "memory_ma", "response_ma", "error_ma",
    "cpu_std", "memory_std", "response_std",
    "cpu_change", "memory_change", "response_change", "error_change",
    "cpu_lag1", "cpu_lag2",
    "memory_lag1", "memory_lag2",
    "response_lag1", "response_lag2",
    "error_lag1", "error_lag2"
]

X = df[feature_cols]

# -------------------------------
# LOAD MODELS
# -------------------------------
anomaly_bundle = joblib.load(ANOMALY_MODEL_FILE)
anomaly_model = anomaly_bundle["model"]
anomaly_scaler = anomaly_bundle["scaler"]

pred_bundle = joblib.load(PRED_MODEL_FILE)
pred_model = pred_bundle["model"]
pred_features = pred_bundle["features"]

root_bundle = joblib.load(ROOT_MODEL_FILE)
root_model = root_bundle["model"]
root_features = root_bundle["features"]

print("✅ All models loaded successfully!")

# -------------------------------
# 1) ANOMALY DETECTION
# -------------------------------
X_scaled = anomaly_scaler.transform(X)
anomaly_pred = anomaly_model.predict(X_scaled)

df["anomaly_label"] = (anomaly_pred == -1).astype(int)
df["anomaly_score"] = anomaly_model.decision_function(X_scaled)

# -------------------------------
# 2) INCIDENT PREDICTION
# -------------------------------
X_pred = df[pred_features] if set(pred_features).issubset(df.columns) else df[feature_cols + ["anomaly_label", "anomaly_score"]]
df["failure_probability"] = pred_model.predict_proba(X_pred)[:, 1]
df["predicted_failure"] = pred_model.predict(X_pred)

# -------------------------------
# 3) ROOT CAUSE PREDICTION
# -------------------------------
# Only predict root cause when predicted_failure = 1
df["predicted_root_cause"] = "NORMAL"

incident_rows = df[df["predicted_failure"] == 1]
if len(incident_rows) > 0:
    X_root = incident_rows[root_features]
    df.loc[df["predicted_failure"] == 1, "predicted_root_cause"] = root_model.predict(X_root)

# -------------------------------
# 4) DECISION ENGINE RULE
# -------------------------------
# Decision threshold
THRESHOLD = 0.70

df["alert_status"] = df["failure_probability"].apply(lambda x: "ALERT" if x >= THRESHOLD else "OK")

# Recommended action based on root cause
def recommend_action(root):
    if root == "CPU_OVERLOAD":
        return "Scale up CPU / Restart overloaded service"
    if root == "MEMORY_LEAK":
        return "Restart service / Check memory leak deployment"
    if root == "LATENCY_SPIKE":
        return "Check network / API latency / Load balancer"
    return "No action needed"

df["recommended_action"] = df["predicted_root_cause"].apply(recommend_action)

# Automatic resolution model output
resolution_output = df.apply(
    lambda row: recommend_resolution(
        root_cause=row.get("predicted_root_cause", "NORMAL"),
        cpu_usage=float(row.get("cpu_usage", 0)),
        memory_usage=float(row.get("memory_usage", 0)),
        response_time=float(row.get("response_time", 0)),
        anomaly_score=float(row.get("anomaly_score", 0)),
        failure_probability=float(row.get("failure_probability", 0)),
        anomaly_label=int(row.get("anomaly_label", 0)),
    ),
    axis=1,
    result_type="expand",
)

df = pd.concat([df, resolution_output], axis=1)

def derive_incident_state(row):
    status = str(row.get("resolution_status", "MONITORING"))
    if status == "AUTO_REMEDIATION_EXECUTED":
        return "RESOLVED_BY_AI"
    if status == "MANUAL_INTERVENTION_REQUIRED":
        return "ESCALATED_TO_SRE"
    return "MONITORING"

# Set explicit incident state for dashboard alerts
df["incident_state"] = df.apply(derive_incident_state, axis=1)

# -------------------------------
# SAVE FINAL OUTPUT
# -------------------------------
df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Decision Engine Completed!")
print("📁 Final output saved to:", OUTPUT_FILE)

print("\n📌 Alert Distribution:")
print(df["alert_status"].value_counts())

print("\n📌 Sample Alerts:")
print(df[df["alert_status"] == "ALERT"][[
    "timestamp", "cpu_usage", "memory_usage", "response_time",
    "failure_probability", "predicted_root_cause", "recommended_action"
]].head(10))