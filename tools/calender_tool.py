from agents.linkedinContentGen import setup_llm
from langchain_google_community.calendar.create_event import CalendarCreateEvent
from dotenv import load_dotenv
from utils.calender_event import generate_event

load_dotenv()

def calender_event(user_input: str):
    event = generate_event(user_input)
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
    return {"success": True, "message": "Event created successfully"}