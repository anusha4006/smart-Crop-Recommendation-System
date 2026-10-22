"""
Weather Service: Fetches real-time and seasonal meteorological parameters (Temperature, Humidity, Rainfall)
without requiring physical on-field IoT sensors, using Open-Meteo's Open Meteorological API.
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

# Fallback climatological averages for common regions (in case of network interruption)
FALLBACK_CLIMATE = {
    "bangalore": {"temperature": 24.5, "humidity": 68.0, "rainfall": 85.0},
    "hyderabad": {"temperature": 28.0, "humidity": 55.0, "rainfall": 72.0},
    "chennai": {"temperature": 30.5, "humidity": 78.0, "rainfall": 120.0},
    "mumbai": {"temperature": 29.0, "humidity": 82.0, "rainfall": 180.0},
    "delhi": {"temperature": 26.0, "humidity": 58.0, "rainfall": 65.0},
    "kolkata": {"temperature": 28.5, "humidity": 76.0, "rainfall": 145.0},
    "pune": {"temperature": 25.5, "humidity": 64.0, "rainfall": 90.0},
    "jaipur": {"temperature": 27.5, "humidity": 42.0, "rainfall": 45.0},
    "lucknow": {"temperature": 26.5, "humidity": 62.0, "rainfall": 80.0},
    "chandigarh": {"temperature": 24.0, "humidity": 60.0, "rainfall": 75.0},
    "bhopal": {"temperature": 26.0, "humidity": 56.0, "rainfall": 88.0},
    "kochi": {"temperature": 28.5, "humidity": 84.0, "rainfall": 210.0},
    "default": {"temperature": 25.0, "humidity": 65.0, "rainfall": 95.0}
}

def geocode_city(city_name: str):
    """
    Find coordinates and state for a city name using Open-Meteo Geocoding API.
    """
    clean_city = city_name.strip()
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_city}&count=5&language=en&format=json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "results" in data and len(data["results"]) > 0:
                best = data["results"][0]
                return {
                    "found": True,
                    "name": best.get("name"),
                    "latitude": best.get("latitude"),
                    "longitude": best.get("longitude"),
                    "country": best.get("country", ""),
                    "state": best.get("admin1", ""),
                    "elevation": best.get("elevation", 0)
                }
    except Exception as e:
        logger.warning(f"Geocoding failed for {city_name}: {e}")
    return {"found": False, "name": clean_city}

def fetch_weather_by_coords(lat: float, lon: float):
    """
    Fetch current temperature, relative humidity, and precipitation data
    from Open-Meteo Forecast API.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,relative_humidity_2m,precipitation,weather_code&"
        f"daily=precipitation_sum,temperature_2m_max,temperature_2m_min&"
        f"timezone=auto"
    )
    try:
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})

            temp = curr.get("temperature_2m", 25.0)
            humidity = curr.get("relative_humidity_2m", 65.0)

            # Estimate normal seasonal / 30-day precipitation in mm for crop modeling:
            # 7-day precipitation sum scaled to monthly/seasonal scale for agricultural baseline
            daily_precip = daily.get("precipitation_sum", [0.0])
            sum_precip_7d = sum(daily_precip) if daily_precip else 5.0
            # Normalize to agricultural dataset rainfall scale (typically 40 - 250 mm)
            estimated_rainfall = max(35.0, min(280.0, round(sum_precip_7d * 4.2 + 40.0, 1)))

            return {
                "success": True,
                "temperature": round(float(temp), 1),
                "humidity": round(float(humidity), 1),
                "rainfall": estimated_rainfall,
                "source": "Open-Meteo Satellite / Weather API (Real-Time)"
            }
    except Exception as e:
        logger.warning(f"Open-Meteo API call failed: {e}")

    return None

def get_weather_for_location(city_name: str = None, lat: float = None, lon: float = None):
    """
    Unified method to get weather without sensors.
    """
    location_meta = {}
    if city_name:
        geo = geocode_city(city_name)
        if geo["found"]:
            lat = geo["latitude"]
            lon = geo["longitude"]
            location_meta = geo

    if lat is not None and lon is not None:
        weather = fetch_weather_by_coords(lat, lon)
        if weather:
            weather.update({"latitude": lat, "longitude": lon, "location_meta": location_meta})
            return weather

    # Fallback if network issue or unknown city
    key = city_name.lower() if city_name else "default"
    fallback_val = FALLBACK_CLIMATE.get(key, FALLBACK_CLIMATE["default"])
    return {
        "success": True,
        "temperature": fallback_val["temperature"],
        "humidity": fallback_val["humidity"],
        "rainfall": fallback_val["rainfall"],
        "source": "Agro-Climatic Regional Averages (Offline Fallback)",
        "location_meta": {"name": city_name or "Regional Center"}
    }
