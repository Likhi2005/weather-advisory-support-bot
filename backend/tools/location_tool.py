import os
from langchain_core.tools import tool
import requests

@tool
def location_resolve_tool(location: str) -> dict:
    """
    Resolve a location or city name to its corresponding latitude and longitude using the Open-Meteo API.
    """
    
    try:
        response = requests.get(
            f"{os.environ.get('METEO_GEOCODING_API_URL')}",
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        results = data.get("results",[])
        
        if not results:
            return {
                "error": f"Could not resolve location: {location}"
            }
            
        result = results[0]
        return {
            "location": location,
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "country": result.get("country"),
            "admin1": result.get("admin1"),
        }
    except requests.Timeout:
        return {
            "error": "Location service request timed out."
        }

    except requests.RequestException as e:
        return {
            "error": f"Location service error: {str(e)}"
        }

    except ValueError:
        return {
            "error": "Invalid response received from location service."
        }