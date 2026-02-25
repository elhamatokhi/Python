import os
import requests
import json
import time
from datetime import datetime

"""
EU Capitals Weather Data Collector
Fetches current weather and hourly forcasts from the Open-Meteo API and stores the results in a structured JSON file.
"""

# EU capital city reference data
eu_capitals = [
   {"city": "Vienna", "country": "Austria", "lat": 48.2082, "lon": 16.3738},
    {"city": "Brussels", "country": "Belgium", "lat": 50.8503, "lon": 4.3517},
    {"city": "Sofia", "country": "Bulgaria", "lat": 42.6977, "lon": 23.3219},
    {"city": "Zagreb", "country": "Croatia", "lat": 45.8150, "lon": 15.9819},
    {"city": "Nicosia", "country": "Cyprus", "lat": 35.1856, "lon": 33.3823},
    {"city": "Prague", "country": "Czechia", "lat": 50.0755, "lon": 14.4378},
    {"city": "Copenhagen", "country": "Denmark", "lat": 55.6761, "lon": 12.5683},
    {"city": "Tallinn", "country": "Estonia", "lat": 59.4370, "lon": 24.7536},
    {"city": "Helsinki", "country": "Finland", "lat": 60.1695, "lon": 24.9354},
    {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
    {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050},
    {"city": "Athens", "country": "Greece", "lat": 37.9838, "lon": 23.7275},
    {"city": "Budapest", "country": "Hungary", "lat": 47.4979, "lon": 19.0402},
    {"city": "Dublin", "country": "Ireland", "lat": 53.3498, "lon": -6.2603},
    {"city": "Rome", "country": "Italy", "lat": 41.9028, "lon": 12.4964},
    {"city": "Riga", "country": "Latvia", "lat": 56.9496, "lon": 24.1052},
    {"city": "Vilnius", "country": "Lithuania", "lat": 54.6872, "lon": 25.2797},
    {"city": "Luxembourg", "country": "Luxembourg", "lat": 49.6116, "lon": 6.1319},
    {"city": "Valletta", "country": "Malta", "lat": 35.8989, "lon": 14.5146},
    {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lon": 4.9041},
    {"city": "Warsaw", "country": "Poland", "lat": 52.2297, "lon": 21.0122},
    {"city": "Lisbon", "country": "Portugal", "lat": 38.7223, "lon": -9.1393},
    {"city": "Bucharest", "country": "Romania", "lat": 44.4268, "lon": 26.1025},
    {"city": "Bratislava", "country": "Slovakia", "lat": 48.1486, "lon": 17.1077},
    {"city": "Ljubljana", "country": "Slovenia", "lat": 46.0569, "lon": 14.5058},
    {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lon": -3.7038},
    {"city": "Stockholm", "country": "Sweden", "lat": 59.3293, "lon": 18.0686}
]

# Base API endpoint
API_URL = "https://api.open-meteo.com/v1/forecast"

# Store final weather data
weather_data = {}

# Iterate through each capital city
for capital in eu_capitals:
    city_name = capital["city"]
    print(f"Fetching weather data form {city_name}...")

    try:
        # Build request parameters
        params = {
            "latitude": capital["lat"],
            "longitude": capital["lon"],
            "current_weather": True,
            "hourly": "temperature_2m,precipitation_probability,weathercode",
            "timezone": "auto"
        }

        # Perfrom API request
        respose = requests.get(API_URL, params=params, timeout=10)
        respose.raise_for_status()
        data = respose.json()

        # Extract current weather safely
        current = data.get("current_weather",{})
        hourly = data.get("hourly",{})

        # Build structured city data
        weather_data[city_name] = {
            "country": capital["country"],
            "coordinates":{
                "latitude": capital["lat"],
                "longitude": capital["lon"]
            },
            "current_weather":{
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "weathercode": current.get("weathercode"),
                "time": current.get("time")
            },
            "hourly_forecast":[]
        }

         # Combine hourly forecast values
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        precip = hourly.get("precipitation_probability", [])
        codes = hourly.get("weathercode", [])

        for i in range(len(times)):
            weather_data[city_name]["hourle_forecast"].append({
                "time": times[i],
                "temperature": temps[i],
                "perciptation_probability": precip[i],
                "weathercode": code[i]
            })
        print(f"Data collected successfully for {city_name}")

    except requests.exceptions.RequestException as e:
        # Handle network_related errors
        print(f'Network error for {city_name}: {e}')

    except (KeyError, TypeError, ValueError) as e:
        # Handle malformed or missing data
        print(f'Data parsig error for {city_name}: {e}')
    
    # Delay to repect API rate limits
    time.sleep(0.7)

# Get directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build full path for output file
output_path = os.path.join(script_dir, "eu_weather_data.json")

# Write collected data to JSON file
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(weather_data, file, indent=4)

print("\nWeather data collection complete.")
print("Output saved to eu_weather_data.json")