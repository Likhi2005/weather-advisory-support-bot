from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from graph.state import AgentState
from tools.location_tool import location_resolve_tool


location_tool_node = ToolNode([location_resolve_tool])

from graph.nodes import (
    understand_query,
    evaluate_tools,
    generate_response,
    weather_failed,
    no_sop
)


def route_after_understand(state: AgentState):
    messages = state.get("messages", [])

    if not messages:
        return "evaluate_tools"

    last_message = messages[-1]

    if getattr(last_message, "tool_calls", None):
        return "location_tool"

    return "evaluate_tools"


def route_after_tools(state: AgentState):
    if state.get("error"):
        return "weather_failed"

    if not state.get("matched_sops"):
        return "no_sop"
    return "generate_response"

def build_graph():
    graph = StateGraph(AgentState)
    
    # nodes
    graph.add_node("understand_query",understand_query)
    graph.add_node("location_tool", location_tool_node)
    graph.add_node("evaluate_tools",evaluate_tools)
    graph.add_node("generate_response",generate_response)
    
    # failure nodes
    graph.add_node("weather_failed", weather_failed)
    graph.add_node("no_sop", no_sop)
    
    # edges
    graph.add_edge(START, "understand_query")
    
    # Conditional Branching based on tool execution results
    graph.add_conditional_edges(
        "understand_query",
        route_after_understand,
        {
            "location_tool": "location_tool",
            "evaluate_tools": "evaluate_tools",
        },
    )

    
    graph.add_edge(
        "location_tool",
        "evaluate_tools",
    )
    
    
    graph.add_conditional_edges(
        "evaluate_tools",
        route_after_tools,
        {
            "weather_failed": "weather_failed",
            "no_sop": "no_sop",
            "generate_response": "generate_response",
        },
    )
    
    # END states
    graph.add_edge("generate_response", END)
    graph.add_edge("weather_failed", END)
    graph.add_edge("no_sop", END)
    
    return graph.compile()