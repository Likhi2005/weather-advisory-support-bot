from dotenv import load_dotenv
from pathlib import Path
from fastapi.responses import FileResponse

load_dotenv()


from fastapi import FastAPI
app = FastAPI(title="Weather Advisory Support Bot")

# Importing the required modules
from schemas.chat import ChatRequest, ChatResponse
from graph.workflow import build_graph

# Build the workflow graph
graph = build_graph()

@app.get("/")
def serve_frontend():
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    return FileResponse(frontend_path)


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
    

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = graph.invoke({
        "user_query": request.message
    })

    return ChatResponse(
        response=result["response"]
    )
