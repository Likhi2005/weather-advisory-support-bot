import json

from graph.state import AgentState
from tools.weather_tool import weather_tool
from tools.sop_tool import sop_tool
from tools.location_tool import location_resolve_tool
from llm.client import llm


def understand_query(state: AgentState):
    user_query = state["user_query"]

    prompt = f"""
You are a Query Understanding Component for a weather safety Advisor system.

Extract only information explicitly stated. Do not infer or assume anything.

User request: {user_query}

Extract:
- location: City or location mentioned by the user.
- activity: Outdoor activity such as cycling, running, hiking, walking, outdoor_exercise, picnic, camping, etc.
- intent: Purpose of the request.
  Examples: outdoor_activity, travel, commute, picnic
- transport: motorcycle, scooter, bicycle, car, etc.
- user_group: elderly, senior, child, children, pet, dog, cat, etc.
- time: today, this afternoon, evening, tomorrow, next week, etc.

Do not invent information.
If something is not present, return null for that field.

Return ONLY valid JSON.
Do not use markdown.
Do not add explanations.

Example:
{{
    "location": null,
    "activity": null,
    "intent": null,
    "transport": null,
    "user_group": null,
    "time": null
}}
"""

    try:
        result = llm.invoke(prompt)
        content = result.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        intent = json.loads(content)

    except Exception as e:
        return {
            "error": f"Could not understand the user request: {str(e)}"
        }

    if not intent.get("location"):
        return {
            "intent": intent,
            "error": "Location was not provided."
        }

    return {
        "intent": intent
    }


def process_location(state: AgentState):
    intent = state.get("intent", {})
    location = intent.get("location")

    if not location:
        return {
            "error": "Location was not provided."
        }

    try:
        data = location_resolve_tool.invoke({
            "location": location
        })
    except Exception as e:
        return {
            "error": str(e)
        }

    if not isinstance(data, dict):
        return {
            "error": "Invalid location response."
        }

    if data.get("error"):
        return {
            "error": data["error"]
        }

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return {
            "error": "Location could not be resolved."
        }

    return {
        "location": data,
        "latitude": latitude,
        "longitude": longitude
    }


def evaluate_tools(state: AgentState):
    latitude = state.get("latitude")
    longitude = state.get("longitude")
    intent = state.get("intent", {})

    print("INTENT:", intent)
    print("LATITUDE:", latitude)
    print("LONGITUDE:", longitude)

    if latitude is None or longitude is None:
        return {
            "error": "Location could not be resolved."
        }

    weather_result = weather_tool.invoke({
        "latitude": latitude,
        "longitude": longitude
    })

    print("WEATHER:", weather_result)

    if "error" in weather_result:
        return {
            "error": weather_result["error"]
        }

    sop_result = sop_tool.invoke({
        "weather": weather_result,
        "intent": intent
    })

    print("SOP RESULT:", sop_result)

    if isinstance(sop_result, dict) and "error" in sop_result:
        return {
            "error": sop_result["error"]
        }

    return {
        "weather": weather_result,
        "matched_sops": sop_result
    }


def generate_response(state: AgentState):
    user_query = state.get("user_query", "")
    weather = state.get("weather", {})
    matched_sops = state.get("matched_sops", [])

    prompt = f"""
You are the response generation component of a weather safety advisory system.

Generate a concise answer to the user's question.

Strict rules:

- Use ONLY the weather data provided below.
- Never invent or estimate weather values.
- Use ONLY the guidance from the matched SOPs.
- Do not create your own safety advice.
- Always mention the SOP ID when an SOP applies.
- Explain the recommendation naturally.
- Do not claim that a policy exists when it does not.

User question:
{user_query}

Actual weather data:
{weather}

Matched SOPs:
{matched_sops}
"""

    result = llm.invoke(prompt)

    return {
        "response": result.content
    }


def weather_failed(state: AgentState):
    return {
        "response": (
            "I couldn't retrieve the current weather data at the moment. "
            "So I can't provide a weather-based recommendation. "
            "Please try again later."
        )
    }


def no_sop(state: AgentState):
    user_query = state.get("user_query", "")

    prompt = f"""
You are a weather safety advisory assistant.

The user's request was:
{user_query}

The policy engine found no matching safety policy.

Tell the user politely that there is currently no
applicable guidance in the configured safety policies.

Do not provide your own safety advice.
Do not guess.
Do not claim that an SOP applies.
Keep the response concise.
"""

    result = llm.invoke(prompt)

    return {
        "response": result.content
    }