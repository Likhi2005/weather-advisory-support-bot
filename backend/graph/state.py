from typing import TypedDict, Optional
class AgentState(TypedDict, total=False):
    user_query: str
    messages: list
    longitude: float
    latitude: float
    intent: dict
    location: dict
    weather: dict
    matched_sops: list
    response: str
    error: str