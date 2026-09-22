from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
app = FastAPI(title="Weather Advisory Support Bot")


@app.get("/")
def main():
    return {"message": "Welcome to the Weather Advisory Support Bot!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/weather/{latitude}/{longitude}")
def get_weather(latitude: float, longitude: float):
    from services.weather_service import WeatherService
    
    weather_service = WeatherService()
    try:
        weather_data = weather_service.get_weather(latitude, longitude)
        return {"weather_data": weather_data}
    except Exception as e:
        return {"error": str(e)}
