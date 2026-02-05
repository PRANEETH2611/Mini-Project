import os
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# -------------------------------
# PATH SETUP
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "metrics_features.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "anomaly_output.csv")
MODEL_FILE = os.path.join(BASE_DIR, "models", "isolation_forest.pkl")

# Ensure folders exist
os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(INPUT_FILE)

print("✅ Loaded processed dataset:", df.shape)
print(df.head(2))

# -------------------------------
# SELECT FEATURES FOR ANOMALY DETECTION
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
# SCALE FEATURES
# -------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------------
# TRAIN ISOLATION FOREST
# -------------------------------
model = IsolationForest(
    n_estimators=200,
    contamination=0.15,   # 15% anomalies (you can tune this)
    random_state=42
)
model.fit(X_scaled)

# -------------------------------
# PREDICT ANOMALIES
# -------------------------------
# IsolationForest gives: -1 (anomaly), 1 (normal)
pred = model.predict(X_scaled)

# Convert to 0/1 format
df["anomaly_label"] = (pred == -1).astype(int)

# Anomaly score: lower = more anomalous
df["anomaly_score"] = model.decision_function(X_scaled)

# -------------------------------
# SAVE RESULTS + MODEL
# -------------------------------
df.to_csv(OUTPUT_FILE, index=False)

# Save model + scaler together
joblib.dump({"model": model, "scaler": scaler, "features": feature_cols}, MODEL_FILE)

print("\n✅ Anomaly Detection Completed!")
print("📁 Output saved to:", OUTPUT_FILE)
print("💾 Model saved to:", MODEL_FILE)

print("\n📌 Anomaly distribution:")
print(df["anomaly_label"].value_counts())

print("\n📌 Sample anomaly rows:")
print(df[df["anomaly_label"] == 1].head(5)[
    ["timestamp", "cpu_usage", "memory_usage", "response_time", "error_count", "anomaly_label", "anomaly_score"]
])
