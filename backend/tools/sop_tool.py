from langchain_core.tools import tool

from services.sop_service import SOPService


sop_service = SOPService()


@tool
def sop_tool(weather: dict, intent: dict) -> list:
    """Evaluate the configured SOP rules against
    the actual weather data and user intent."""
    
    try:
        return sop_service.evaluate_rule(
            weather=weather,
            intent=intent
        )
    except Exception as e:
        return {"error": str(e)}