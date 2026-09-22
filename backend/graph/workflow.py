from langgraph.graph import StateGraph, START, END
from graph.state import AgentState

from graph.nodes import (
    evaluate_sops,
)

def route_after_weather(state: AgentState):
    if state.get("error"):
        return "weather_failed"
    
    return "evaluate_sops"

def route_after_sop(state: AgentState):
    if not state.get("matched_sops"):
        return "no sop"
    return "generate_response"

def build_graph():
    graph = StateGraph(AgentState)
    
    # nodes
    graph.add_node(START, "start")
    graph.add_node("evaluate_sops", evaluate_sops)
    graph.add_node(END, "end")
    
    # edges
    graph.add_edge(START, "----")
    graph.add_edge("___", END)