from langgraph.graph import StateGraph, END, START

from app.core.state import InterviewState
from app.core.nodes import (
    tech_node,
    pressure_node,
    comprehensive_node,
)

STAGES = ["INIT", "TECH", "PRESSURE", "COMPREHENSIVE", "DONE"]
MAX_ROUNDS_PER_STAGE = 8


def _route_entry(state: InterviewState) -> str:
    stage = state.get("stage", "TECH")
    mapping = {
        "TECH": "tech",
        "PRESSURE": "pressure",
        "COMPREHENSIVE": "comprehensive",
    }
    return mapping.get(stage, "tech")


def build_interview_graph() -> StateGraph:
    graph = StateGraph(InterviewState)

    graph.add_node("tech", tech_node)
    graph.add_node("pressure", pressure_node)
    graph.add_node("comprehensive", comprehensive_node)

    graph.add_conditional_edges(
        START,
        _route_entry,
        {"tech": "tech", "pressure": "pressure", "comprehensive": "comprehensive"}
    )

    graph.add_edge("tech", END)
    graph.add_edge("pressure", END)
    graph.add_edge("comprehensive", END)

    return graph.compile()


interview_graph = build_interview_graph()
