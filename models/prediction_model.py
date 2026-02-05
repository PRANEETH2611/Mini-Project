import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# -------------------------------
# PATH SETUP
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "anomaly_output.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "prediction_output.csv")
MODEL_FILE = os.path.join(BASE_DIR, "models", "incident_prediction_model.pkl")

# Ensure folders exist
os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(INPUT_FILE)

print("✅ Loaded anomaly dataset:", df.shape)
print(df.head(2))

# -------------------------------
# SELECT FEATURES + TARGET
# -------------------------------
feature_cols = [
    "cpu_usage", "memory_usage", "response_time", "error_count",
    "cpu_ma", "memory_ma", "response_ma", "error_ma",
    "cpu_std", "memory_std", "response_std",
    "cpu_change", "memory_change", "response_change", "error_change",
    "cpu_lag1", "cpu_lag2",
    "memory_lag1", "memory_lag2",
    "response_lag1", "response_lag2",
    "error_lag1", "error_lag2",
    "anomaly_label", "anomaly_score"
]

X = df[feature_cols]
y = df["failure"]

# -------------------------------
# SPLIT TRAIN / TEST
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print("\n✅ Train size:", X_train.shape)
print("✅ Test size:", X_test.shape)

# -------------------------------
# TRAIN RANDOM FOREST MODEL
# -------------------------------
model = RandomForestClassifier(
    n_estimators=250,
    max_depth=None,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# -------------------------------
# PREDICT
# -------------------------------
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # failure probability

# -------------------------------
# EVALUATION
# -------------------------------
print("\n✅ Model Evaluation:")
print("Accuracy:", accuracy_score(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------
# SAVE MODEL
# -------------------------------
joblib.dump({"model": model, "features": feature_cols}, MODEL_FILE)
print("\n💾 Model saved to:", MODEL_FILE)

# -------------------------------
# SAVE PREDICTION RESULTS
# -------------------------------
results_df = X_test.copy()
results_df["actual_failure"] = y_test.values
results_df["predicted_failure"] = y_pred
results_df["failure_probability"] = y_prob

results_df.to_csv(OUTPUT_FILE, index=False)

print("📁 Prediction output saved to:", OUTPUT_FILE)
print("\n✅ Sample Predictions:")
print(results_df.head(10)[["actual_failure", "predicted_failure", "failure_probability"]])
