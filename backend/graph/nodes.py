from graph.state import AgentState
from models.query import UserIntent
from tools.weather_tool import weather_tool
from tools.sop_tool import sop_tool
from tools.location_tool import location_resolve_tool
from langgraph.prebuilt import ToolNode
from llm.client import llm

# tools = [weather_tool, sop_tool]

# tool_node = ToolNode(tools)

intent_llm = llm.with_structured_output(UserIntent)

location_llm = llm.bind_tools([
    location_resolve_tool
])


def understand_query(state: AgentState):
    """
    Understand the users natural Language question and convert it into structured data.
    """
    
    user_query = state["user_query"]
    
    prompt = f"""
    You are a Query Understanding Component for a weather safety Advisor system.
    Extract only information explicitly stated. Do not infer or assume any information.
    
    User request: {user_query}
    
    Extract:
    - location: City or location mnetioned By the user.
    - activity: Outdoor activity such as cycling,running,hiking,walking,outdoor_exercise,picnic, camping. etc
    - intent: purpose of the request
        Examples:
        outdoor_activity,travel,commute,picnic
    - transport:
        motorcycle,scooter,bicycle,car, etc.
    - user_group:
        elderly,senior,child,children,pet,dog,cat,etc.
    - time:
        today, this afternoon, evening, tomorrow, next week, etc.

    
    Do not invent information If something is not present, return null for that field.
    """
    
    result = intent_llm.invoke(prompt)
    
    intent = result.model_dump()
    
    location = intent.get("location")
    
    if not location:
        return {
            "intent": intent,
            "error": "Location was not provided."
        }
    
    location_prompt = f"""
    The user provided this location:

    {location}

    Resolve this location using the location_resolve_tool.

    Do not invent latitude or longitude.
    """

    location_result = location_llm.invoke(location_prompt)

    return {
        "intent": intent,
        "messages": [location_result],
    }

    

def evaluate_tools(state: AgentState):
    """
    Fetch weather data and evaluate the configured SOPs.

    Weather data comes from the weather tool.
    SOP matching is performed by the SOP tool.
    """
    latitude = state.get("latitude")
    longitude = state.get("longitude")
    intent = state.get("intent", {})

    if latitude is None or longitude is None:
        return {
            "error": "Location could not be resolved."
        }

    #Fetch live weather
    weather_result = weather_tool.invoke({
        "latitude": latitude,
        "longitude": longitude
    })

    if "error" in weather_result:
        return {
            "error": weather_result["error"]
        }

    #Evaluate SOP
    sop_result = sop_tool.invoke({
        "weather": weather_result,
        "intent": intent
    })

    if isinstance(sop_result, dict) and "error" in sop_result:
        return {
            "error": sop_result["error"]
        }

    return {
        "weather": weather_result,
        "matched_sops": sop_result
    }



def generate_response(state: AgentState):
    """
    Generate the final response Using only:
    - actual weather data
    - matched SOPs
    - users original query
    
    The llm must not invent safety advice or weather facts.
    """
    user_query = state.get("user_query", "")
    weather = state.get("weather",{})
    matched_sops=state.get("matched_sops", [])
    
    prompt = f"""
    You are the response generation component of a weather
    safety advisory system.

    Generate a concise answer to the user's question.

    Strict rules:

    - Use ONLY the weather data provided below.
    - Never invent or estimate weather values.
    - Use ONLY the guidance from the matched SOPs.
    - Do not create your own safety advice.
    - Always mention the SOP ID when an SOP applies.
    - Explain the recommendation naturally.
    - If no SOP applies, clearly tell the user that there is
    no applicable guidance in the current safety policies.
    - Do not claim that a policy exists when it does not.
    - Do not make a recommendation that is not supported by
    a matched SOP.

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
    """
    Handle the case when the weather tool fails to fetch data.
    OR Handle weather API failure
    """
    
    return {
        "response": (
            "I couldn't retrieve the current weather data at the moment."
            "So I cant provide a weather-based recommendation. Please try again later."
        )
    }
    
def no_sop(state: AgentState):
    """
    Generate a response when no configured SOP matches.
    """
    user_query=state.get("user_query", "")

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