from flask import Flask, request, jsonify
import requests
import os
import hashlib
import redis
import json
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Optional, Dict

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.getenv("DEFAULT_RATE_LIMIT", "10 per minute")]
)

# Configuration from environment
API_KEY = os.getenv("API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

# Redis client setup
redis_client = redis.Redis.from_url(REDIS_URL)


def build_url(location: str, api_key: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Build the API URL for the weather service.
    """
    if start_date and end_date:
        return (
            f"{BASE_URL}/{location}/{start_date}/{end_date}"
            f"?key={api_key}&unitGroup=metric&include=days&contentType=json"
        )
    return f"{BASE_URL}/{location}?key={api_key}&unitGroup=metric&include=days&contentType=json"


def get_cache_key(params: Dict) -> str:
    """
    Generate a unique cache key from query parameters.
    """
    key_string = json.dumps(params, sort_keys=True)
    return f"weather:{hashlib.md5(key_string.encode()).hexdigest()}"


def fetch_weather_data(url: str) -> Dict:
    """
    Make an external request to the weather API.
    """
    response = requests.get(url)
    if response.status_code == 400:
        raise requests.HTTPError("Bad Request: Invalid parameters.", response=response)
    elif response.status_code == 401:
        raise requests.HTTPError("Unauthorized: Invalid or missing API key.", response=response)
    elif response.status_code == 404:
        raise requests.HTTPError("Not Found: Endpoint or resource does not exist.", response=response)
    elif response.status_code == 429:
        raise requests.HTTPError("Too Many Requests: Rate limit exceeded.", response=response)
    elif response.status_code >= 500:
        raise requests.HTTPError("Internal Server Error: Problem with the external service.", response=response)

    response.raise_for_status()
    return response.json()

@app.route("/weather", methods=["GET"])
@limiter.limit("5 per minute")
def get_weather():
    """
    Weather endpoint: Returns cached or fresh weather data based on query params.
    """
    location = request.args.get("location")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not location:
        return jsonify({"error": "Location is required"}), 400

    if not API_KEY:
        return jsonify({"error": "API_KEY not set"}), 500

    params = {"location": location, "start_date": start_date, "end_date": end_date}
    cache_key = get_cache_key(params)

    # Try to retrieve from Redis cache
    cached = redis_client.get(cache_key)
    if cached:
        return jsonify(json.loads(cached))

    # If not cached, fetch from API and cache result
    try:
        url = build_url(location, API_KEY, start_date, end_date)
        data = fetch_weather_data(url)
        redis_client.setex(cache_key, 600, json.dumps(data))  # Cache for 10 minutes
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
