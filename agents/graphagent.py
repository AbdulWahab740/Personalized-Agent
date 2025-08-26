from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.linkedinAnalyticsGraph import profile_analytics_agent
from agents.linkedinAnalytics import analyze_post_agent
from tools.content_postingTool import content_posting_agent
from agents.email_graph import graph as email_graph
from agents.calender_graph import calender_graph
from agents.linkedinContentGen import setup_llm
from agents.content_graph import graph as content_graph
class AgentState(TypedDict):
    query: str
    choice: str   # linkedin_post / profile_analytics / post_analytics / email / calender / compound
    uploaded_file_path: Optional[str]
    output: Optional[dict]
    route: Optional[str]
    compound_actions: Optional[list]  # For handling multiple actions

maingraph = StateGraph(AgentState)

# Router (MainAgent) - LangChain-based intelligent routing
def router(state: AgentState) -> AgentState:
    llm = setup_llm()
    
    prompt = f"""You are an intelligent routing agent. Based on the user's query, determine which agent should handle the request.

Available agents:
1. linkedin_post - Creates LinkedIn posts and content
2. profile_analytics - Analyzes profile data from Excel/CSV files
3. post_analytics - Analyzes existing LinkedIn posts from URLs
4. email - Generates and sends emails
5. calender - Creates events on Google Calendar
6. compound - Handles multiple actions in sequence (e.g., "create calendar event and send email")

User query: "{state['query']}"

Routing guidance and examples:
- If the user asks for "best performing post", "top post(s)", "top performing", or similar analytics insights, choose profile_analytics (these rely on uploaded Excel/CSV analytics files).
- If the user provides a LinkedIn post URL or asks to analyze a specific URL, choose post_analytics.
- If the query involves multiple actions (like creating calendar event AND sending email), respond with "compound".
Otherwise, respond with ONLY the single agent name (linkedin_post, profile_analytics, post_analytics, email, or calender).
"""
    
    response = llm.invoke(prompt)
    choice = response.content.strip().lower() if hasattr(response, 'content') else str(response).strip().lower()
    
    # Validate the choice
    valid_choices = ["linkedin_post", "profile_analytics", "post_analytics", "email", "calender", "compound"]
    if choice not in valid_choices:
        # Fallback to keyword matching if LLM gives invalid response
        q = state["query"].lower()
        # Check for compound requests first
        if ("calender" in q or "event" in q) and ("email" in q or "mail" in q):
            choice = "compound"
        elif "linkedin post" in q or "create post" in q:
            choice = "linkedin_post"
        elif (
            "profile analytics" in q or "excel" in q or "sheet" in q or
            "best performing" in q or "top post" in q or "top posts" in q or "top-performing" in q or "best post" in q
        ):
            choice = "profile_analytics"
        elif "analyze post" in q or "url" in q:
            choice = "post_analytics"
        elif "email" in q or "send mail" in q:
            choice = "email"
        elif "calender" in q or "event" in q:
            choice = "calender"
        else:
            choice = "linkedin_post"  # default fallback
    
    return {"route": choice}

maingraph.add_node("router", router)

# LinkedIn Post Agent
def linkedin_post_agent(state: AgentState) -> AgentState:
    # call your existing linkedin post creation + upload toolchain
    content_state = {
        "query": state["query"],
        "content": None,
        "approved": False,
        "output": None
    }
    content_comp = content_graph.compile()
    output = content_comp.invoke(content_state, start_at="draft")
    return {"output": output, "route": "content"}

# Profile Analytics Agent
def profile_analytic_agent(state: AgentState) -> AgentState:
    # Guard: ensure an analytics file is provided
    file_path = state.get("uploaded_file_path")
    if not file_path:
        return {"output": {"success": False, "error": "No analytics file provided. Please upload your LinkedIn analytics Excel/CSV file."}, "route": "profile_analytics"}
    output = profile_analytics_agent(file_path, state["query"])
    return {"output": output, "route": "profile_analytics"}

# Post Analytics Agent
def post_analytics_agent(state: AgentState) -> AgentState:
    # Guard: require a LinkedIn post URL for post analytics
    q = state.get("query", "") or ""
    if not ("linkedin.com" in q or q.strip().startswith("http")):
        return {"output": {"success": False, "error": "Post analysis expects a LinkedIn post URL. Try asking for 'best performing post' to use profile analytics, or provide a specific post URL."}, "route": "post_analytics"}
    output = analyze_post_agent(q)
    return {"output": output, "route": "post_analytics"}

# Email Agent
def email_agent(state: AgentState) -> AgentState:
    # Use the email_graph for complete email workflow
    email_state = {
        "query": state["query"],
        "draft": None,
        "approved": False,
        "output": None
    }
    
    # Compile and run the email graph starting from draft generation
    email_comp = email_graph.compile()
    result = email_comp.invoke(email_state, start_at="draft")
    
    # Return the draft for review (not automatically sending)
    return {"output": {"draft": result["draft"], "status": "draft_generated"}, "route": "email"}

def calender_agent(state: AgentState) -> AgentState:
    calender_event = {
        "query": state["query"],
        "output": None
    }
    calender_comp = calender_graph.compile()
    output = calender_comp.invoke(calender_event, start_at="generate_event")
    return {"output": output, "route": "calender"}

# Compound Agent - handles multiple actions sequentially
def compound_agent(state: AgentState) -> AgentState:
    """Handle compound requests like 'create calendar event and send email'"""
    query = state["query"]
    results = {}
    
    # Check if query involves calendar and email
    q_lower = query.lower()
    if ("calender" in q_lower or "event" in q_lower) and ("email" in q_lower or "mail" in q_lower):
        # Step 1: Create calendar event
        calender_event = {
            "query": query,
            "output": None
        }
        calender_comp = calender_graph.compile()
        calendar_result = calender_comp.invoke(calender_event, start_at="generate_event")
        results["calendar"] = calendar_result
        
        # Step 2: Generate and send email about the calendar event
        # Extract event details for email context with proper null checks
        output_data = calendar_result.get("output") if calendar_result else None
        event_info = output_data.get("event", {}) if output_data else {}
        
        # Safely extract event details
        summary = event_info.get('summary', 'New Event') if event_info else 'New Event'
        start_info = event_info.get('start', {}) if event_info else {}
        start_time = start_info.get('dateTime', 'TBD') if isinstance(start_info, dict) else 'TBD'
        
        email_query = f"Send an email about the calendar event: {summary} scheduled for {start_time}"
        
        email_state = {
            "query": email_query,
            "draft": None,
            "approved": False,
            "output": None
        }
        
        # Generate email draft
        email_comp = email_graph.compile()
        email_draft_result = email_comp.invoke(email_state, start_at="draft")
        
        # Auto-approve and send the email with null checks
        if email_draft_result and email_draft_result.get("draft"):
            email_send_state = {
                "query": email_query,
                "draft": email_draft_result["draft"],
                "approved": True,
                "output": None
            }
            email_result = email_comp.invoke(email_send_state, start_at="send")
            results["email"] = email_result
        else:
            results["email"] = {"output": {"success": False, "error": "Failed to generate email draft"}}
        
        return {"output": results, "route": "compound"}
    
    # Fallback for other compound requests
    return {"output": {"error": "Compound request not recognized"}, "route": "compound"}

# Add nodes
maingraph.add_node("linkedin_post", linkedin_post_agent)
maingraph.add_node("profile_analytics", profile_analytic_agent)
maingraph.add_node("post_analytics", post_analytics_agent)
maingraph.add_node("email", email_agent)
maingraph.add_node("calender", calender_agent)
maingraph.add_node("compound", compound_agent)

# Routing function for conditional edges
def route_to_agent(state: AgentState) -> str:
    """Route to the appropriate agent based on the choice made by the router."""
    return state["route"]

# Conditional edges from router to specific agents
maingraph.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "linkedin_post": "linkedin_post",
        "profile_analytics": "profile_analytics", 
        "post_analytics": "post_analytics",
        "email": "email",
        "calender": "calender",
        "compound": "compound"
    }
)

# All agents end at the END node
maingraph.add_edge("linkedin_post", END)
maingraph.add_edge("profile_analytics", END)
maingraph.add_edge("post_analytics", END)
maingraph.add_edge("email", END)
maingraph.add_edge("calender", END)
maingraph.add_edge("compound", END)

maingraph.set_entry_point("router")
