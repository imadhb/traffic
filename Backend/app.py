from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@app.route('/api/traffic/predict', methods=['GET'])
def predict_traffic():
    # Get query parameters
    origin = request.args.get('origin')  # Starting point
    destination = request.args.get('destination')  # Ending point
    
    if not origin or not destination:
        return jsonify({"error": "Origin and destination are required"}), 400

    # Make a request to the Google Directions API
    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params={
                "origin": origin,
                "destination": destination,
                "key": GOOGLE_MAPS_API_KEY,
                "departure_time": "now",  # Real-time traffic data
            }
        )
        data = response.json()

        # Parse the API response to extract traffic information
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            legs = route.get("legs", [])[0]
            duration = legs.get("duration", {}).get("text", "Unknown")
            duration_in_traffic = legs.get("duration_in_traffic", {}).get("text", "Unknown")
            return jsonify({
                "origin": origin,
                "destination": destination,
                "duration": duration,
                "duration_in_traffic": duration_in_traffic,
            })
        else:
            return jsonify({"error": "No route found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
