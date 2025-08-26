# # backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_community.calendar.create_event import CalendarCreateEvent
from automation.linkedin_content_automation import LinkedInContentAutomation
from agents.graphagent import maingraph
from agents.email_graph import graph
from typing import Optional
from fastapi import Form
import streamlit as st
from fastapi import Request
# Data model matching frontend's request
class QueryRequest(BaseModel):
    query: str
    file_path: Optional[str] = None  # Optional path to uploaded file

app = FastAPI(
    title="Personal Content Agent WhatsApp Bot",
    description="WhatsApp bot for LinkedIn content generation",
    version="1.0.0"
)

# Allow all origins for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_response")
async def get_linkedin_post(req: QueryRequest):
    try:
        main = maingraph.compile()
        query = main.invoke({"query": req.query, "uploaded_file_path": req.file_path,"choice":""})
        if "email" == query["route"]:
            return {"message": query, "status": "draft_generated"}
        elif "content" == query["route"]:
            return {"message": query, "status": "content_generated"}
        elif "calender" == query["route"]:
            print("Got the query: ", query)
            return {"message": query, "status": "calender_generated"}
        elif "compound" == query["route"]:
            print("Got compound query: ", query)
            return {"message": query, "status": "compound_completed"}
        print(f"DEBUG RESULT: {query}")  
        return {"message": query}        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_linkedin_post: {error_details}")
        return {"error": str(e), "message": "An error occurred while processing your request."}


@app.post("/send_email")
def send_email(req: dict):
    draft = req.get("draft")
    if not draft:
        return {"output": {"success": False, "error": "Draft missing"}}

    state = {
        "query": "",           
        "draft": draft,        
        "approved": True,
        "output": None
    }
    comp = graph.compile()
    result = comp.invoke(state, start_at="send")
    if result.get("draft", {}).get("to") == "default@example.com":
        print("Graph corrupted draft, using direct send")
        from automation.mail_send import gmail_send_message
        direct_result = gmail_send_message(draft["subject"], draft["body"], draft["to"])
        return {"output": direct_result}

    return {"output": result.get("output", {"success": False, "error": "No output from graph"})}


@app.post("/post_content")
def post_content(req: dict):
    content = req.get("content")
    if not content:
        return {"output": {"success": False, "error": "Content missing"}}
    
    automation = LinkedInContentAutomation()
    automation.create_post(content)
    return {"output": {"success": True, "result": "Submitted Successfully"}}

@app.post("/create_event")
def create_event(req: dict):
    event = req.get("event")
    if not event:
        return {"output": {"success": False, "error": "Event missing"}}
    
    tool = CalendarCreateEvent()
    tool.invoke(
        {
            "summary": event["summary"],
            "start_datetime": event["start_datetime"],
            "end_datetime": event["end_datetime"],
            "timezone": event["timezone"],
            "location": event["location"],
            "description": event["description"],
            "reminders": event["reminders"],
            "conference_data": event["conference_data"],
            "color_id": event["color_id"],
        }
    )
    return {"output": {"success": True, "result": "Submitted Successfully"}}
