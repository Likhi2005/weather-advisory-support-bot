import os
import requests

class WeatherService:
    def __init__(self):
        self.weather_api_url = os.getenv("METEO_WEATHER_APT_URL")

        if not self.weather_api_url:
            raise ValueError("METEO_WEATHER_APT_URL environment variable is not set.")
    
    def get_weather(self, latitude:float,longitude:float):
        try:
            response = requests.get(
                self.weather_api_url,
                params={"latitude": latitude, "longitude": longitude},
                timeout=10
                )
            
            response.raise_for_status()
            
            return response.json()
        
        except requests.Timeout:
            raise Exception("Request to weather API timed out.")
        
        except requests.RequestException as e:
            raise Exception(f"Error while making request to weather API: {e}")
        
        except ValueError:
            raise Exception("Invalid response received from weather API.")