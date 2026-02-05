import joblib
import pandas as pd
import matplotlib.pyplot as plt

model_data = joblib.load("models/incident_prediction_model.pkl")
model = model_data["model"]
features = model_data["features"]

importances = model.feature_importances_
fi = pd.DataFrame({"feature": features, "importance": importances})
fi = fi.sort_values(by="importance", ascending=False).head(10)

plt.figure(figsize=(10,4))
plt.bar(fi["feature"], fi["importance"])
plt.xticks(rotation=45)
plt.title("Top 10 Feature Importances (Incident Prediction)")
plt.grid(True)
plt.show()
