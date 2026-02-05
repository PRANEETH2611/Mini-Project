import os
import pandas as pd
import numpy as np

# -------------------------------
# CONFIGURATION
# -------------------------------
np.random.seed(42)

TOTAL_POINTS = 1500          # total minutes of data
NORMAL_RATIO = 0.7           # 70% normal, 30% incidents

# Incident types
INCIDENT_TYPES = ["CPU_OVERLOAD", "MEMORY_LEAK", "LATENCY_SPIKE"]

# -------------------------------
# OUTPUT PATH (PERMANENT FIX)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "cloud_metrics.csv")

# Create folders if missing
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# -------------------------------
# GENERATE TIMESTAMPS
# -------------------------------
timestamps = pd.date_range(start="2025-01-01", periods=TOTAL_POINTS, freq="min")

normal_points = int(TOTAL_POINTS * NORMAL_RATIO)
incident_points = TOTAL_POINTS - normal_points

# -------------------------------
# NORMAL BEHAVIOR
# -------------------------------
cpu_normal = np.random.normal(loc=45, scale=6, size=normal_points)
mem_normal = np.random.normal(loc=4.0, scale=0.6, size=normal_points)
latency_normal = np.random.normal(loc=200, scale=50, size=normal_points)
error_normal = np.random.poisson(lam=1, size=normal_points)

failure_normal = np.zeros(normal_points)  # 0 = no failure
root_normal = ["NORMAL"] * normal_points

# -------------------------------
# INCIDENT BEHAVIOR (MIXED TYPES)
# -------------------------------
cpu_incident = []
mem_incident = []
latency_incident = []
error_incident = []
root_incident = []

for _ in range(incident_points):
    incident = np.random.choice(INCIDENT_TYPES)

    if incident == "CPU_OVERLOAD":
        cpu_incident.append(np.random.normal(loc=92, scale=4))
        mem_incident.append(np.random.normal(loc=5.0, scale=0.7))
        latency_incident.append(np.random.normal(loc=800, scale=150))
        error_incident.append(np.random.poisson(lam=10))
        root_incident.append("CPU_OVERLOAD")

    elif incident == "MEMORY_LEAK":
        cpu_incident.append(np.random.normal(loc=65, scale=8))
        mem_incident.append(np.random.normal(loc=9.0, scale=0.6))
        latency_incident.append(np.random.normal(loc=500, scale=120))
        error_incident.append(np.random.poisson(lam=12))
        root_incident.append("MEMORY_LEAK")

    elif incident == "LATENCY_SPIKE":
        cpu_incident.append(np.random.normal(loc=55, scale=7))
        mem_incident.append(np.random.normal(loc=5.0, scale=0.6))
        latency_incident.append(np.random.normal(loc=3200, scale=400))
        error_incident.append(np.random.poisson(lam=20))
        root_incident.append("LATENCY_SPIKE")

# Convert to numpy arrays
cpu_incident = np.array(cpu_incident)
mem_incident = np.array(mem_incident)
latency_incident = np.array(latency_incident)
error_incident = np.array(error_incident)

failure_incident = np.ones(incident_points)  # 1 = incident

# -------------------------------
# COMBINE NORMAL + INCIDENT
# -------------------------------
cpu = np.concatenate([cpu_normal, cpu_incident])
memory = np.concatenate([mem_normal, mem_incident])
latency = np.concatenate([latency_normal, latency_incident])
errors = np.concatenate([error_normal, error_incident])

failure = np.concatenate([failure_normal, failure_incident])
root_cause = root_normal + root_incident

# Safety clipping
cpu = np.clip(cpu, 0, 100)
memory = np.clip(memory, 0, None)
latency = np.clip(latency, 0, None)

# -------------------------------
# CREATE FINAL DATAFRAME
# -------------------------------
df = pd.DataFrame({
    "timestamp": timestamps,
    "cpu_usage": cpu.round(2),
    "memory_usage": memory.round(2),
    "response_time": latency.round(2),
    "error_count": errors.astype(int),
    "failure": failure.astype(int),
    "root_cause": root_cause
})

# Shuffle rows so incidents are mixed
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# -------------------------------
# SAVE CSV
# -------------------------------
df.to_csv(OUTPUT_FILE, index=False)

print("✅ Fake cloud metrics dataset generated successfully!")
print(f"📁 Saved to: {OUTPUT_FILE}")

print("\n📌 Dataset Preview:")
print(df.head(10))

print("\n📌 Root Cause Distribution:")
print(df["root_cause"].value_counts())
