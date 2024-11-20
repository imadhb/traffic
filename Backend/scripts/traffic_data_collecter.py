import requests
import csv
import time
from math import radians, cos, sin, sqrt, atan2
from dotenv import load_dotenv
import os


load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTES_FILE = os.path.join(BASE_DIR, "routes.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "traffic_data.csv")

try:
    with open(OUTPUT_FILE, "x", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "origin",
            "destination",
            "origin_lat",
            "origin_lng",
            "destination_lat",
            "destination_lng",
            "travel_time",
            "traffic_time",
            "hour",
            "day_of_week",
            "distance"
        ])
except FileExistsError:
    print(f"{OUTPUT_FILE} already exists. Appending data.")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# Function to fetch traffic data
def fetch_traffic_data():
    """Fetch traffic data for each route."""
    try:
        with open(ROUTES_FILE, "r") as file:
            routes = [
                {"origin": line.split("->")[0].strip(), "destination": line.split("->")[1].strip()}
                for line in file.readlines()
                if "->" in line
            ]
    except FileNotFoundError:
        print(f"Error: Routes file not found at {ROUTES_FILE}")
        return

    for route in routes:
        origin = route["origin"]
        destination = route["destination"]

        try:
            # Make a request to the Google Maps Directions API
            url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data["status"] == "OK":
                leg = data["routes"][0]["legs"][0]
                travel_time = leg["duration"]["value"]  # Travel time in seconds
                traffic_time = leg.get("duration_in_traffic", {}).get("value", travel_time)

                # Extract coordinates
                origin_coords = leg["start_location"]
                destination_coords = leg["end_location"]

                # Calculate distance
                distance = haversine(
                    origin_coords["lat"], origin_coords["lng"],
                    destination_coords["lat"], destination_coords["lng"]
                )

                # Get the current time
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                hour = time.localtime().tm_hour
                day_of_week = time.localtime().tm_wday  # 0 = Monday, 6 = Sunday

                # Write the data to the CSV file
                with open(OUTPUT_FILE, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        timestamp,
                        origin,
                        destination,
                        origin_coords["lat"],
                        origin_coords["lng"],
                        destination_coords["lat"],
                        destination_coords["lng"],
                        travel_time,
                        traffic_time,
                        hour,
                        day_of_week,
                        distance
                    ])

                print(f"Data logged for {origin} -> {destination} at {timestamp}")
            else:
                print(f"Error for {origin} -> {destination}: {data['status']}")

        except Exception as e:
            print(f"Error fetching data for {origin} -> {destination}: {e}")

if __name__ == "__main__":
    # Fetch traffic data every 5 minutes
    while True:
        fetch_traffic_data()
        print("Sleeping for 5 minutes...")
        time.sleep(300)  # Wait 5 minutes before the next fetch
