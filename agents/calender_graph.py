from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from utils.calender_event import generate_event

class CalenderState(TypedDict):
    query: str
    output: Optional[dict]

calender_graph = StateGraph(CalenderState)

# Step 1: Generate Draft
def generate_event_draft(state: CalenderState) -> CalenderState:
    event_data = generate_event(state["query"])
    return {"output": {"event": event_data}}

calender_graph.add_node("generate_event", generate_event_draft)
calender_graph.add_edge("generate_event", END)
calender_graph.set_entry_point("generate_event")
