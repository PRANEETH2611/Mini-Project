import os
import pandas as pd
import numpy as np

# -------------------------------
# PATH SETUP (PERMANENT FIX)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "cloud_metrics.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "metrics_features.csv")

# Create processed folder if missing
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(INPUT_FILE)

print("✅ Loaded dataset successfully!")
print("Shape:", df.shape)
print(df.head())

# -------------------------------
# DATA CLEANING
# -------------------------------
# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort by timestamp (important for time-series features)
df = df.sort_values("timestamp").reset_index(drop=True)

# -------------------------------
# FEATURE ENGINEERING
# -------------------------------

# Rolling window size (in minutes)
WINDOW = 5

# ✅ Moving averages
df["cpu_ma"] = df["cpu_usage"].rolling(window=WINDOW).mean()
df["memory_ma"] = df["memory_usage"].rolling(window=WINDOW).mean()
df["response_ma"] = df["response_time"].rolling(window=WINDOW).mean()
df["error_ma"] = df["error_count"].rolling(window=WINDOW).mean()

# ✅ Rolling standard deviation
df["cpu_std"] = df["cpu_usage"].rolling(window=WINDOW).std()
df["memory_std"] = df["memory_usage"].rolling(window=WINDOW).std()
df["response_std"] = df["response_time"].rolling(window=WINDOW).std()

# ✅ Rate of change (difference)
df["cpu_change"] = df["cpu_usage"].diff()
df["memory_change"] = df["memory_usage"].diff()
df["response_change"] = df["response_time"].diff()
df["error_change"] = df["error_count"].diff()

# ✅ Lag features (previous values)
df["cpu_lag1"] = df["cpu_usage"].shift(1)
df["cpu_lag2"] = df["cpu_usage"].shift(2)

df["memory_lag1"] = df["memory_usage"].shift(1)
df["memory_lag2"] = df["memory_usage"].shift(2)

df["response_lag1"] = df["response_time"].shift(1)
df["response_lag2"] = df["response_time"].shift(2)

df["error_lag1"] = df["error_count"].shift(1)
df["error_lag2"] = df["error_count"].shift(2)

# -------------------------------
# HANDLE NaN VALUES
# -------------------------------
# First few rows will become NaN due to rolling and lag
df = df.dropna().reset_index(drop=True)

# -------------------------------
# SAVE PROCESSED DATA
# -------------------------------
df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Feature Engineering Completed!")
print("✅ Processed dataset saved at:")
print(OUTPUT_FILE)
print("Final shape:", df.shape)

print("\n📌 Preview of processed dataset:")
print(df.head(10))
