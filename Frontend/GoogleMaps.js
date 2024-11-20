import React, { useState } from "react";
import { View, TextInput, FlatList, TouchableOpacity, Button, StyleSheet, Text, Alert } from "react-native";
import MapView, { Marker, Polyline } from "react-native-maps";
import { GOOGLE_MAPS_API_KEY } from "@env";

const GoogleMapsScreen = () => {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [originAutocompleteResults, setOriginAutocompleteResults] = useState([]);
  const [destinationAutocompleteResults, setDestinationAutocompleteResults] = useState([]);
  const [originCoords, setOriginCoords] = useState(null);
  const [destinationCoords, setDestinationCoords] = useState(null);
  const [routeCoordinates, setRouteCoordinates] = useState([]);

  const fetchAutocompleteResults = async (input, setResults) => {
    if (!input) {
      setResults([]);
      return;
    }
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${input}&key=${GOOGLE_MAPS_API_KEY}`
      );
      const data = await response.json();
      if (data.predictions) {
        setResults(data.predictions);
      } else {
        setResults([]);
      }
    } catch (error) {
      console.error("Error fetching autocomplete results:", error);
    }
  };

  const fetchPlaceDetails = async (placeId, setCoords) => {
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&key=${GOOGLE_MAPS_API_KEY}`
      );
      const data = await response.json();
      const location = data.result.geometry.location;
      setCoords({ latitude: location.lat, longitude: location.lng });
    } catch (error) {
      console.error("Error fetching place details:", error);
    }
  };

  const getDirections = async () => {
    if (!originCoords || !destinationCoords) {
      Alert.alert("Error", "Please select both origin and destination.");
      return;
    }
  
    try {
      // Fetch directions from Google Maps API
      const directionsResponse = await fetch(
        `https://maps.googleapis.com/maps/api/directions/json?origin=${originCoords.latitude},${originCoords.longitude}&destination=${destinationCoords.latitude},${destinationCoords.longitude}&departure_time=now&key=${GOOGLE_MAPS_API_KEY}`
      );
      const directionsData = await directionsResponse.json();
  
      if (directionsData.routes.length > 0) {
        const points = directionsData.routes[0].overview_polyline.points;
        setRouteCoordinates(decodePolyline(points));
  
        const routeInfo = directionsData.routes[0].legs[0]; // First leg of the route
        const duration = routeInfo.duration.text; // Duration in human-readable format
        const durationInTraffic = routeInfo.duration_in_traffic
          ? routeInfo.duration_in_traffic.text
          : "N/A";
  
        // Fetch AI-based prediction from backend
        const predictionResponse = await fetch("http://10.0.2.2:5000/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            origin,
            destination,
            originCoords,
            destinationCoords,
          }),
        });
        const predictionData = await predictionResponse.json();
  
        // Convert predicted traffic time from seconds to minutes
        const predictedTimeInMinutes = predictionData.predicted_traffic_time
          ? Math.max(0, Math.round(predictionData.predicted_traffic_time / 60))
          : "N/A";
  
        Alert.alert(
          "Traffic Information",
          `Estimated time: ${duration}\nTime with traffic: ${durationInTraffic}\nPredicted Traffic Time (AI): ${predictedTimeInMinutes} minutes`
        );
      } else {
        Alert.alert("Error", "No route found.");
      }
    } catch (error) {
      console.error("Error fetching directions or predictions:", error);
      Alert.alert("Error", "Failed to fetch traffic information.");
    }
  };
  

  const decodePolyline = (encoded) => {
    let points = [];
    let index = 0,
      len = encoded.length;
    let lat = 0,
      lng = 0;

    while (index < len) {
      let b, shift = 0,
        result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      let dlat = result & 1 ? ~(result >> 1) : result >> 1;
      lat += dlat;

      shift = 0;
      result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      let dlng = result & 1 ? ~(result >> 1) : result >> 1;
      lng += dlng;

      points.push({
        latitude: lat / 1e5,
        longitude: lng / 1e5,
      });
    }
    return points;
  };

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: 42.3314,
          longitude: -83.0458,
          latitudeDelta: 0.5,
          longitudeDelta: 0.5,
        }}
        showsTraffic
      >
        {originCoords && <Marker coordinate={originCoords} title="Origin" />}
        {destinationCoords && <Marker coordinate={destinationCoords} title="Destination" />}
        {routeCoordinates.length > 0 && (
          <Polyline coordinates={routeCoordinates} strokeColor="#FF0000" strokeWidth={4} />
        )}
      </MapView>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Enter Origin"
          value={origin}
          onChangeText={(text) => {
            setOrigin(text);
            fetchAutocompleteResults(text, setOriginAutocompleteResults);
          }}
        />
        <FlatList
          data={originAutocompleteResults}
          keyExtractor={(item) => item.place_id}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() => {
                fetchPlaceDetails(item.place_id, setOriginCoords);
                setOrigin(item.description);
                setOriginAutocompleteResults([]);
              }}
            >
              <Text style={styles.autocompleteItem}>{item.description}</Text>
            </TouchableOpacity>
          )}
        />
        <TextInput
          style={styles.input}
          placeholder="Enter Destination"
          value={destination}
          onChangeText={(text) => {
            setDestination(text);
            fetchAutocompleteResults(text, setDestinationAutocompleteResults);
          }}
        />
        <FlatList
          data={destinationAutocompleteResults}
          keyExtractor={(item) => item.place_id}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() => {
                fetchPlaceDetails(item.place_id, setDestinationCoords);
                setDestination(item.description);
                setDestinationAutocompleteResults([]);
              }}
            >
              <Text style={styles.autocompleteItem}>{item.description}</Text>
            </TouchableOpacity>
          )}
        />
        <Button title="Get Directions with Traffic" onPress={getDirections} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  inputContainer: {
    position: "absolute",
    bottom: 0,
    width: "100%",
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    padding: 10,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  input: {
    height: 40,
    borderColor: "gray",
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 8,
    borderRadius: 5,
  },
  autocompleteItem: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
  },
});

export default GoogleMapsScreen;
