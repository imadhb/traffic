import pandas as pd
import os

# Path to the CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "traffic_data.csv")
CLEANED_CSV_FILE = os.path.join(BASE_DIR, "cleaned_traffic_data.csv")

# Load the CSV file
try:
    data = pd.read_csv(CSV_FILE)
    print(f"Data loaded from {CSV_FILE}")
except FileNotFoundError:
    print(f"Error: File not found at {CSV_FILE}")
    exit()

# Check for negative or zero values in traffic_time and travel_time
print("Cleaning invalid data...")
data = data[(data["traffic_time"] > 0) & (data["travel_time"] > 0)]

# Check for other anomalies (optional)
# For example, you can drop rows where distance is 0 or very small
data = data[data["distance"] > 0.1]

# Save the cleaned data
data.to_csv(CLEANED_CSV_FILE, index=False)
print(f"Cleaned data saved to {CLEANED_CSV_FILE}")
