from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
import os

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "scripts", "cleaned_traffic_data.csv")
MODEL_FILE = os.path.join(BASE_DIR,"traffic_model.pkl")

# Load dataset
data = pd.read_csv(DATA_FILE)

# Features and target
features = data[["origin_lat", "origin_lng", "destination_lat", "destination_lng", "travel_time", "traffic_time", "distance"]]
target = data["traffic_time"]

# Scale features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(scaled_features, target, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")
print(f"Mean Squared Error: {mse}")

# Save model and scaler
joblib.dump({"model": model, "scaler": scaler}, MODEL_FILE)
print(f"Model saved to {MODEL_FILE}")
