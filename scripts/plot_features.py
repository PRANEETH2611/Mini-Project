import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/metrics_features.csv")

plt.figure(figsize=(10,4))
df["cpu_usage"].head(200).plot(label="CPU Usage")
df["cpu_ma"].head(200).plot(label="CPU Moving Avg")
plt.title("CPU Usage vs Moving Average")
plt.legend()
plt.grid(True)
plt.show()
