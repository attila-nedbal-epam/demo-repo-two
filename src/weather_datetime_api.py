from flask import Flask, jsonify, request
from datetime import datetime, timezone
from typing import Dict, Any
import os
import requests
import json
import logging
import pytz
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
class Config:
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    BUDAPEST_LAT = 47.49798
    BUDAPEST_LON = 19.040235
    DEFAULT_TIMEZONE = 'Europe/Budapest'

class WeatherService:
    @staticmethod
    def get_weather_data(lat: float, lon: float, api_key: str) -> Dict[Any, Any]:
        """
        Fetch weather data from OpenWeatherMap API
        """
        if not api_key:
            return {

                "error": "Weather API key not configured",
                "temperature": "N/A",
                "description": "Weather data unavailable",
                "humidity": "N/A",
                "wind_speed": "N/A"
            }
        
        url = f"{Config.OPENWEATHER_BASE_URL}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'  # Celsius, m/s
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temperature": data['main']['temp'],
                "feels_like": data['main']['feels_like'],
                "description": data['weather'][0]['description'].title(),
                "humidity": data['main']['humidity'],
                "pressure": data['main']['pressure'],
                "wind_speed": data['wind']['speed'],
                "wind_direction": data['wind']['deg'],
                "cloudiness": data['clouds']['all'],
                "visibility": data.get('visibility', 'N/A'),
                "city": data['name'],
                "country": data['sys']['country']
            }
        except requests.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return {
                "error": f"Weather API request failed: {str(e)}",
                "temperature": "N/A",
                "description": "Weather data unavailable",
                "humidity": "N/A",
                "wind_speed": "N/A"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "error": f"Unexpected error: {str(e)}",
                "temperature": "N/A",
                "description": "Weather data unavailable",
                "humidity": "N/A",
                "wind_speed": "N/A"
            }

class DateTimeService:
    @staticmethod
    def get_current_datetime(timezone_str: str = Config.DEFAULT_TIMEZONE) -> Dict[Any, Any]:
        """
        Get current date and time information
        """
        try:
            # Get UTC time
            utc_now = datetime.now(timezone.utc)
            
            # Get local time for Budapest
            budapest_tz = pytz.timezone(timezone_str)
            local_now = utc_now.astimezone(budapest_tz)
            
            return {
                "current_datetime_utc": str(utc_now.isoformat()),
                "current_datetime_local": str(local_now.isoformat()),
                "timestamp": int(utc_now.timestamp()),
                "timezone": timezone_str,
                "date": str(local_now.date()),
                "time": str(local_now.time()),
                "weekday": local_now.strftime('%A'),
                "month": local_now.strftime('%B %Y')
            }
        except Exception as e:
            logger.error(f"DateTime error: {e}")
            return {
                "error": f"DateTime error: {str(e)}"
            }

# API Routes
@app.route('/api/datetime', methods=['GET'])
def get_datetime():
    """
    Get current date and time information
    """
    try:
        datetime_data = DateTimeService.get_current_datetime()
        
        response = {
            "status": "success",
            "message": "Date and time retrieved successfully",
            "data": datetime_data
        }
        
        logger.info("DateTime API request successful")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"DateTime API error: {e}")
        return jsonify({
            "status": "error",
            "message": f"DateTime API error: {str(e)}"
        }), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Get weather information for Budapest
    """
    try:
        # Get optional parameters
        lat = float(request.args.get('lat', Config.BUDAPEST_LAT))
        lon = float(request.args.get('lon', Config.BUDAPEST_LON))
        
        weather_data = WeatherService.get_weather_data(lat, lon, Config.OPENWEATHER_API_KEY)
        
        response = {
            "status": "success",
            "message": "Weather data retrieved successfully",
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "data": weather_data
        }
        
        logger.info(f"Weather API request successful for lat: {lat}, lon: {lon}")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.error(f"Invalid coordinates: {e}")
        return jsonify({
            "status": "error",
            "message": f"Invalid coordinates: {str(e)}"
        }), 400
        
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Weather API error: {str(e)}"
        }), 500

@app.route('/api/combined', methods=['GET'])
def get_combined():
    """
    Get combined datetime and weather information for Budapest
    """
    try:
        # Get optional parameters
        lat = float(request.args.get('lat', Config.BUDAPEST_LAT))
        lon = float(request.args.get('lon', Config.BUDAPEST_LON))
        
        # Get datetime and weather data
        datetime_data = DateTimeService.get_current_datetime()
        weather_data = WeatherService.get_weather_data(lat, lon, Config.OPENWEATHER_API_KEY)
        
        response = {
            "status": "success",
            "message": "Combined datetime and weather data retrieved successfully",
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "datetime": datetime_data,
            "weather": weather_data
        }
        
        logger.info(f"Combined API request successful for lat: {lat}, lon: {lon}")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.error(f"Invalid coordinates: {e}")
        return jsonify({
            "status": "error",
            "message": f"Invalid coordinates: {str(e)}"
        }), 400
        
    except Exception as e:
        logger.error(f"Combined API error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Combined API error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "ok",
        "message": "Weather Datetime API is running",
        "timestamp": str(datetime.now(timezone.utc).isoformat()),
        "version": "1.0.0"
    }), 200

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with API documentation
    """
    api_doc = {
        "name": "Weather Datetime API",
        "version": "1.0.0",
        "description": "API that provides current date/time and weather information for Budapest",
        "endpoints": {
            "GET /api/datetime": {
                "description": "Get current date and time information",
                "parameters": "None"
            },
            "GET /api/weather": {
                "description": "Get weather information for Budapest",
                "parameters": "lat (optional), lon (optional)"
            },
            "GET /api/combined": {
                "description": "Get combined datetime and weather information",
                "parameters": "lat (optional), lon (optional)"
            },
            "GET /api/health": {
                "description": "Health check endpoint",
                "parameters": "None"
            }
        },
        "examples": {
            "DateTime": "curl http://localhost:5000/api/datetime",
            "Weather": "curl http://localhost:5000/api/weather",
            "Combined": "curl http://localhost:5000/api/combined",
            "Health": "curl http://localhost:5000/api/health"
        }
    }
    
    return jsonify(api_doc), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            "/api/datetime",
            "/api/weather",
            "/api/combined",
            "/api/health"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
