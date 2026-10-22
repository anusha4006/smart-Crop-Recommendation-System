"""
Soil Service: Provides Soil pH and Soil Nutrient (N, P, K) characteristics
without physical hardware sensors, based on regional soil maps and geospatial soil taxonomy.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'soil_profiles.json')

def load_soil_profiles():
    try:
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading soil profiles: {e}")
        return {"soil_types": {}, "regional_presets": []}

SOIL_DATA = load_soil_profiles()

def list_soil_types():
    """Returns list of selectable soil types with friendly names and default pH values."""
    types = []
    for key, val in SOIL_DATA.get("soil_types", {}).items():
        types.append({
            "key": key,
            "name": val.get("name"),
            "default_ph": val.get("default_ph"),
            "ph_range": val.get("ph_range"),
            "default_n": val.get("default_n"),
            "default_p": val.get("default_p"),
            "default_k": val.get("default_k"),
            "description": val.get("description"),
            "best_crops": val.get("best_crops")
        })
    return types

def list_regional_presets():
    """Returns list of pre-configured cities/regions with their soil properties."""
    return SOIL_DATA.get("regional_presets", [])

def get_soil_by_city(city_name: str):
    """
    Finds soil pH and nutrients for a given city or district name.
    """
    if not city_name:
        return None
    city_lower = city_name.strip().lower()
    for preset in SOIL_DATA.get("regional_presets", []):
        if preset["city"].lower() in city_lower or city_lower in preset["city"].lower():
            soil_type_info = SOIL_DATA.get("soil_types", {}).get(preset["soil_type"], {})
            return {
                "matched_city": preset["city"],
                "state": preset["state"],
                "soil_type_key": preset["soil_type"],
                "soil_type_name": soil_type_info.get("name", preset["soil_type"]),
                "ph": preset["ph"],
                "n": preset["n"],
                "p": preset["p"],
                "k": preset["k"],
                "source": "Regional Agricultural Soil Survey Database"
            }
    return None

def get_soil_by_type(soil_type_key: str):
    """
    Retrieves soil parameters for a given soil type key.
    """
    types = SOIL_DATA.get("soil_types", {})
    if soil_type_key in types:
        item = types[soil_type_key]
        return {
            "soil_type_key": soil_type_key,
            "soil_type_name": item["name"],
            "ph": item["default_ph"],
            "n": item["default_n"],
            "p": item["default_p"],
            "k": item["default_k"],
            "ph_range": item["ph_range"],
            "description": item["description"],
            "source": "Agro-Soil Classification Standard"
        }
    # Default to Alluvial if unknown
    alluvial = types.get("alluvial", {})
    return {
        "soil_type_key": "alluvial",
        "soil_type_name": alluvial.get("name", "Alluvial Soil"),
        "ph": alluvial.get("default_ph", 7.0),
        "n": alluvial.get("default_n", 70),
        "p": alluvial.get("default_p", 40),
        "k": alluvial.get("default_k", 40),
        "ph_range": [6.5, 7.8],
        "description": "Standard fertile agricultural soil.",
        "source": "Default Soil Taxonomy"
    }
