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
MODEL_FILE = os.path.join(BASE_DIR, "models", "root_cause_model.pkl")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "rootcause_output.csv")

os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(INPUT_FILE)
print("✅ Loaded dataset:", df.shape)
print(df.head(2))

# -------------------------------
# FILTER ONLY INCIDENT ROWS
# -------------------------------
# Root cause is meaningful only when failure=1
df_incident = df[df["failure"] == 1].copy()

print("\n✅ Incident-only dataset:", df_incident.shape)
print("Root Cause Distribution:")
print(df_incident["root_cause"].value_counts())

# -------------------------------
# FEATURES + TARGET
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

X = df_incident[feature_cols]
y = df_incident["root_cause"]

# -------------------------------
# TRAIN/TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("\n✅ Train size:", X_train.shape)
print("✅ Test size:", X_test.shape)

# -------------------------------
# MODEL TRAINING
# -------------------------------
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# -------------------------------
# PREDICTION + EVALUATION
# -------------------------------
y_pred = model.predict(X_test)

print("\n✅ Root Cause Model Evaluation")
print("Accuracy:", accuracy_score(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------
# SAVE MODEL
# -------------------------------
joblib.dump({"model": model, "features": feature_cols}, MODEL_FILE)
print("\n💾 Root cause model saved to:", MODEL_FILE)

# -------------------------------
# SAVE OUTPUT CSV WITH PREDICTIONS
# -------------------------------
results_df = X_test.copy()
results_df["actual_root_cause"] = y_test.values
results_df["predicted_root_cause"] = y_pred

results_df.to_csv(OUTPUT_FILE, index=False)
print("📁 Root cause predictions saved to:", OUTPUT_FILE)

print("\n✅ Sample root cause predictions:")
print(results_df[["actual_root_cause", "predicted_root_cause"]].head(10))
