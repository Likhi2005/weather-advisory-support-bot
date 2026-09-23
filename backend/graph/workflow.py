from langgraph.graph import StateGraph, START, END

from graph.state import AgentState

from graph.nodes import (
    understand_query,
    evaluate_tools,
    process_location,
    generate_response,
    weather_failed,
    no_sop
)


def route_after_understand(state: AgentState):
    if state.get("error"):
        return "weather_failed"

    if state.get("intent", {}).get("location"):
        return "process_location"

    return "weather_failed"


def route_after_tools(state: AgentState):
    if state.get("error"):
        return "weather_failed"

    if not state.get("matched_sops"):
        return "no_sop"

    return "generate_response"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("understand_query", understand_query)
    graph.add_node("process_location", process_location)
    graph.add_node("evaluate_tools", evaluate_tools)
    graph.add_node("generate_response", generate_response)

    graph.add_node("weather_failed", weather_failed)
    graph.add_node("no_sop", no_sop)

    graph.add_edge(START, "understand_query")

    graph.add_conditional_edges(
        "understand_query",
        route_after_understand,
        {
            "process_location": "process_location",
            "weather_failed": "weather_failed"
        }
    )

    graph.add_edge(
        "process_location",
        "evaluate_tools"
    )

    graph.add_conditional_edges(
        "evaluate_tools",
        route_after_tools,
        {
            "weather_failed": "weather_failed",
            "no_sop": "no_sop",
            "generate_response": "generate_response"
        }
    )

    graph.add_edge("generate_response", END)
    graph.add_edge("weather_failed", END)
    graph.add_edge("no_sop", END)

    return graph.compile()