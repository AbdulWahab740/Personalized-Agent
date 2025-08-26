from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.linkedinContentGen import setup_llm, PersonalizedLinkedInContentAgent

content_agent = PersonalizedLinkedInContentAgent()

class ContentState(TypedDict):
    query: str
    content: Optional[str]
    approved: bool
    output: Optional[str]

def content_draft_node(state: ContentState) -> ContentState:
    content = content_agent.generate_personalized_content(state["query"])
    return {"content": content, "approved": False}


graph = StateGraph(ContentState)
graph.add_node("draft", content_draft_node)
graph.set_entry_point("draft")
graph.add_edge("draft", END)