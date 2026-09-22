from typing import TypedDict

class AgentState(TypedDict):
    user_query: str
    longitude: float
    latitude: float
    intent: dict
    location: dict
    weather: dict
    matched_sops: list
    response: str
    error: str