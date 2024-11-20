from flask import Flask, request, jsonify
import requests
import joblib
from math import radians, cos, sin, sqrt, atan2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Define file paths dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend directory
MODEL_FILE = os.path.join(BASE_DIR, "traffic_model.pkl")  # Model file in Backend

# Load your trained ML model
try:
    model = joblib.load(MODEL_FILE)
    print(f"Model loaded from {MODEL_FILE}")
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_FILE}")
    exit()

# Initialize Flask app
app = Flask(__name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon coordinates using the Haversine formula."""
    R = 6371  # Radius of the Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def get_traffic_data_from_google(origin, destination):
    """Fetch real-time traffic data from Google Maps API."""
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        route = data["routes"][0]["legs"][0]
        travel_time = route["duration"]["value"]  # Travel time in seconds
        traffic_time = route.get("duration_in_traffic", {}).get("value", travel_time)  # Traffic time in seconds
        origin_coords = route["start_location"]
        destination_coords = route["end_location"]
        return travel_time, traffic_time, origin_coords, destination_coords
    else:
        raise Exception(f"Google Maps API error: {data['status']}")

@app.route("/predict", methods=["POST"])
def predict_traffic():
    data = request.json
    origin = data.get("origin")
    destination = data.get("destination")
    origin_coords = data.get("originCoords")
    destination_coords = data.get("destinationCoords")

    if not origin or not destination or not origin_coords or not destination_coords:
        return jsonify({"error": "Origin, destination, and coordinates are required"}), 400

    try:
        # Get traffic data and calculate distance
        travel_time, traffic_time, google_origin_coords, google_destination_coords = get_traffic_data_from_google(origin, destination)
        distance = calculate_distance(
            google_origin_coords["lat"],
            google_origin_coords["lng"],
            google_destination_coords["lat"],
            google_destination_coords["lng"],
        )

        # Prepare features
        features = [[
            origin_coords["latitude"],
            origin_coords["longitude"],
            destination_coords["latitude"],
            destination_coords["longitude"],
            travel_time,
            traffic_time,
            distance
        ]]

        # Load model and scaler
        model_data = joblib.load("traffic_model.pkl")
        model = model_data["model"]
        scaler = model_data["scaler"]

        # Scale features
        scaled_features = scaler.transform(features)

        # Predict
        prediction = model.predict(scaled_features)
        return jsonify({
            "predicted_traffic_time": max(0, prediction[0]),  # Ensure non-negative prediction
            "real_time_data": {
                "travel_time": travel_time,
                "traffic_time": traffic_time,
                "distance": distance
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
