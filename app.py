"""
Flask Application: Sensorless Crop Recommendation System
Replaces hardware IoT sensors with Meteorological Open Data APIs and Regional Soil Mapping.
"""

import os
from flask import Flask, render_template, request, jsonify
from services.weather_service import get_weather_for_location, geocode_city
from services.soil_service import get_soil_by_city, get_soil_by_type, list_soil_types, list_regional_presets
from services.recommender import recommend, get_model_metadata, get_crop_details

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sensorless-crop-rec-secret-key-2026'

@app.route('/')
def index():
    soil_types = list_soil_types()
    regional_presets = list_regional_presets()
    metadata = get_model_metadata()
    return render_template('index.html',
                           soil_types=soil_types,
                           presets=regional_presets,
                           metadata=metadata)

@app.route('/api/weather', methods=['GET'])
def api_weather():
    city = request.args.get('city')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if not city and (lat is None or lon is None):
        return jsonify({"error": "Please provide either 'city' or 'lat' and 'lon'"}), 400

    weather = get_weather_for_location(city_name=city, lat=lat, lon=lon)
    soil = get_soil_by_city(city) if city else None

    return jsonify({
        "weather": weather,
        "soil": soil
    })

@app.route('/api/soil', methods=['GET'])
def api_soil():
    soil_type = request.args.get('type')
    city = request.args.get('city')

    if city:
        soil = get_soil_by_city(city)
        if soil:
            return jsonify(soil)

    if soil_type:
        soil = get_soil_by_type(soil_type)
        return jsonify(soil)

    return jsonify({"error": "Provide either 'city' or 'type'"}), 400

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.get_json(silent=True) or request.form

    try:
        temp = float(data.get('temperature'))
        humidity = float(data.get('humidity'))
        ph = float(data.get('ph'))
        rainfall = float(data.get('rainfall'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing parameters (temperature, humidity, ph, rainfall required)"}), 400

    n = data.get('n')
    p = data.get('p')
    k = data.get('k')

    n_val = float(n) if n not in [None, ''] else None
    p_val = float(p) if p not in [None, ''] else None
    k_val = float(k) if k not in [None, ''] else None

    result = recommend(temperature=temp, humidity=humidity, ph=ph, rainfall=rainfall,
                       n=n_val, p=p_val, k=k_val)

    return jsonify(result)

@app.route('/dataset')
def dataset_page():
    metadata = get_model_metadata()
    crops_info = {crop: get_crop_details(crop) for crop in metadata.get('crops', [])}
    return render_template('dataset.html', metadata=metadata, crops_info=crops_info)

@app.route('/sensorless-guide')
def sensorless_guide():
    return render_template('guide.html')

if __name__ == '__main__':
    print("=" * 60)
    print("  Sensorless Crop Recommendation System Running")
    print("  Parameters: Temperature, Humidity, Soil pH, Rainfall")
    print("  Access dashboard: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
