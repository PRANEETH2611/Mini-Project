"""Live model inference utilities for ingest-time cloud metrics classification."""
from __future__ import annotations

import os
import sys
from typing import Any

import joblib
import pandas as pd

# Make local package imports work when used by backend/app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANOMALY_MODEL_FILE = os.path.join(BASE_DIR, "models", "isolation_forest.pkl")
PRED_MODEL_FILE = os.path.join(BASE_DIR, "models", "incident_prediction_model.pkl")
ROOT_MODEL_FILE = os.path.join(BASE_DIR, "models", "root_cause_model.pkl")
RAW_METRIC_COLUMNS = ["timestamp", "cpu_usage", "memory_usage", "response_time", "error_count"]

anomaly_bundle = joblib.load(ANOMALY_MODEL_FILE)
anomaly_model = anomaly_bundle["model"]
anomaly_scaler = anomaly_bundle["scaler"]
anomaly_features = anomaly_bundle["features"]

pred_bundle = joblib.load(PRED_MODEL_FILE)
pred_model = pred_bundle["model"]
pred_features = pred_bundle["features"]

root_bundle = joblib.load(ROOT_MODEL_FILE)
root_model = root_bundle["model"]
root_features = root_bundle["features"]
KNOWN_ROOT_CAUSES = set(root_model.classes_.tolist())
WINDOW = 5


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _prepare_history(existing_df: pd.DataFrame, incoming_row: dict[str, Any]) -> pd.DataFrame:
    history = existing_df.copy()
    for col in RAW_METRIC_COLUMNS:
        if col not in history.columns:
            history[col] = 0

    history = history[RAW_METRIC_COLUMNS].tail(WINDOW + 2).copy()
    new_row = pd.DataFrame([
        {
            "timestamp": pd.to_datetime(incoming_row.get("timestamp"), errors="coerce"),
            "cpu_usage": _safe_float(incoming_row.get("cpu_usage")),
            "memory_usage": _safe_float(incoming_row.get("memory_usage")),
            "response_time": _safe_float(incoming_row.get("response_time")),
            "error_count": int(_safe_float(incoming_row.get("error_count"), 0)),
        }
    ])
    history = pd.concat([history, new_row], ignore_index=True)
    history["timestamp"] = pd.to_datetime(history["timestamp"], errors="coerce")
    history = history.sort_values("timestamp").reset_index(drop=True)
    return history


def _engineer_live_features(history: pd.DataFrame) -> pd.DataFrame:
    df = history.copy()
    df["cpu_ma"] = df["cpu_usage"].rolling(window=WINDOW, min_periods=1).mean()
    df["memory_ma"] = df["memory_usage"].rolling(window=WINDOW, min_periods=1).mean()
    df["response_ma"] = df["response_time"].rolling(window=WINDOW, min_periods=1).mean()
    df["error_ma"] = df["error_count"].rolling(window=WINDOW, min_periods=1).mean()

    df["cpu_std"] = df["cpu_usage"].rolling(window=WINDOW, min_periods=1).std().fillna(0)
    df["memory_std"] = df["memory_usage"].rolling(window=WINDOW, min_periods=1).std().fillna(0)
    df["response_std"] = df["response_time"].rolling(window=WINDOW, min_periods=1).std().fillna(0)

    df["cpu_change"] = df["cpu_usage"].diff().fillna(0)
    df["memory_change"] = df["memory_usage"].diff().fillna(0)
    df["response_change"] = df["response_time"].diff().fillna(0)
    df["error_change"] = df["error_count"].diff().fillna(0)

    df["cpu_lag1"] = df["cpu_usage"].shift(1).fillna(df["cpu_usage"])
    df["cpu_lag2"] = df["cpu_usage"].shift(2).fillna(df["cpu_lag1"])
    df["memory_lag1"] = df["memory_usage"].shift(1).fillna(df["memory_usage"])
    df["memory_lag2"] = df["memory_usage"].shift(2).fillna(df["memory_lag1"])
    df["response_lag1"] = df["response_time"].shift(1).fillna(df["response_time"])
    df["response_lag2"] = df["response_time"].shift(2).fillna(df["response_lag1"])
    df["error_lag1"] = df["error_count"].shift(1).fillna(df["error_count"])
    df["error_lag2"] = df["error_count"].shift(2).fillna(df["error_lag1"])
    return df


def infer_incident(existing_df: pd.DataFrame, incoming_row: dict[str, Any]) -> dict[str, Any]:
    history = _prepare_history(existing_df, incoming_row)
    features_df = _engineer_live_features(history)
    latest = features_df.iloc[[-1]].copy()

    latest_anomaly_x = latest[anomaly_features]
    scaled = anomaly_scaler.transform(latest_anomaly_x)
    anomaly_pred = anomaly_model.predict(scaled)
    anomaly_score = float(anomaly_model.decision_function(scaled)[0])
    anomaly_label = int(anomaly_pred[0] == -1)

    latest["anomaly_label"] = anomaly_label
    latest["anomaly_score"] = anomaly_score

    pred_x = latest[pred_features]
    failure_probability = float(pred_model.predict_proba(pred_x)[0][1])
    predicted_failure = int(pred_model.predict(pred_x)[0])

    root_cause = "NORMAL"
    root_cause_confidence = 1.0 - failure_probability if predicted_failure == 0 else 0.0

    if predicted_failure == 1:
        root_x = latest[root_features]
        root_probs = root_model.predict_proba(root_x)[0]
        best_index = int(root_probs.argmax())
        candidate_root = str(root_model.classes_[best_index])
        root_cause_confidence = float(root_probs[best_index])
        root_cause = candidate_root if root_cause_confidence >= 0.55 else "UNKNOWN_ANOMALY"

        if candidate_root not in KNOWN_ROOT_CAUSES:
            root_cause = "UNKNOWN_ANOMALY"

    alert_status = "ALERT" if predicted_failure == 1 or anomaly_label == 1 else "OK"
    recommended_action = {
        "CPU_OVERLOAD": "Scale up CPU / Restart overloaded service",
        "MEMORY_LEAK": "Restart service / Check memory leak deployment",
        "LATENCY_SPIKE": "Check network / API latency / Load balancer",
        "UNKNOWN_ANOMALY": "Escalate to SRE team for new error investigation",
        "NORMAL": "No action needed",
    }.get(root_cause, "Escalate to SRE team for investigation")

    return {
        **latest.iloc[0][RAW_METRIC_COLUMNS].to_dict(),
        "anomaly_label": anomaly_label,
        "anomaly_score": anomaly_score,
        "failure_probability": failure_probability,
        "predicted_failure": predicted_failure,
        "predicted_root_cause": root_cause,
        "root_cause_confidence": root_cause_confidence,
        "alert_status": alert_status,
        "recommended_action": recommended_action,
        "inference_source": "ml_live_pipeline",
    }
