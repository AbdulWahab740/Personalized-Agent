# email_graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from tools.gmail_tool import gmail_send_message
from tools.email_writer import generate_email_draft  # your LLM draft writer

class EmailState(TypedDict):
    query: str
    draft: Optional[dict]
    approved: bool
    output: Optional[dict]

graph = StateGraph(EmailState)

# Step 1: Generate Draft
def draft_node(state: EmailState) -> EmailState:
    print(f"DEBUG draft_node - input query: '{state['query']}'")
    draft = generate_email_draft(state["query"])  # returns {"to":..., "subject":..., "body":...}
    # print(f"DEBUG draft_node - generated draft: {draft}")
    return {"draft": draft, "approved": False}

# Step 2: Send Email (only if approved)
def send_node(state: EmailState) -> EmailState:
    print(f"DEBUG send_node - received state: {state}")
    draft = state["draft"]
    print(f"DEBUG send_node - draft: {draft}")
    if not draft:
        return {"output": {"success": False, "error": "No draft available"}}
    res = gmail_send_message(draft["subject"], draft["body"], draft["to"])
    # Return the complete state with all fields preserved
    return {
        "query": state["query"],
        "draft": draft,
        "approved": True,
        "output": res
    }

graph.add_node("draft", draft_node)
graph.add_node("send", send_node)

# edges - set draft as default entry point but allow start_at to override
graph.set_entry_point("draft")
graph.add_edge("draft", END)   # stop after draft, wait for review
graph.add_edge("send", END)    # stop after send
