import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/anomaly_output.csv")

# plot CPU and mark anomalies
plt.figure(figsize=(12, 4))
plt.plot(df["cpu_usage"].head(300), label="CPU Usage")

# mark anomaly points
anoms = df[df["anomaly_label"] == 1].head(300).index
plt.scatter(anoms, df.loc[anoms, "cpu_usage"], label="Anomalies", marker="x")

plt.title("CPU Usage with Detected Anomalies")
plt.xlabel("Index")
plt.ylabel("CPU (%)")
plt.legend()
plt.grid(True)
plt.show()
