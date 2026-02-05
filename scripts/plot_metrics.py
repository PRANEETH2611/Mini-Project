import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/raw/cloud_metrics.csv")

plt.figure()
df["cpu_usage"].head(300).plot()
plt.title("CPU Usage Sample")
plt.show()

plt.figure()
df["response_time"].head(300).plot()
plt.title("Response Time Sample")
plt.show()
