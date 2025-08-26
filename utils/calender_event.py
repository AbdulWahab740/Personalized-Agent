from langchain_google_community.calendar.create_event import CalendarCreateEvent
from agents.linkedinContentGen import setup_llm
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import re
load_dotenv()


def generate_event(user_input: str) -> dict:
    """Generate an event on the calendar"""
    llm = setup_llm()
    prompt = PromptTemplate.from_template(
        """You are a calendar event generator.
User input: "{user_input}"
Generate an event on the calendar based on the user input.

Return ONLY in this exact format (no JSON, just key-value pairs):

summary: <event summary>
start_datetime: <event start datetime in YYYY-MM-DD HH:MM:SS format>
end_datetime: <event end datetime in YYYY-MM-DD HH:MM:SS format>
timezone: <event timezone>
location: <event location>
description: <event description>
reminders: popup 60 minutes
conference_data: true
color_id: 5
"""
    )
    chain = prompt | llm
    response_obj = chain.invoke({"user_input": user_input})
    response = response_obj.content
    try:
        summary = re.search(r"summary:\s*(.*)", response).group(1).strip()
        start_datetime = re.search(r"start_datetime:\s*(.*)", response).group(1).strip()
        end_datetime = re.search(r"end_datetime:\s*(.*)", response).group(1).strip()
        timezone = re.search(r"timezone:\s*(.*)", response).group(1).strip()
        location = re.search(r"location:\s*(.*)", response).group(1).strip()
        description = re.search(r"description:\s*(.*)", response).group(1).strip()
        
        # Fixed reminders format
        reminders = [{"method": "popup", "minutes": 60}]
        conference_data = True
        color_id = "5"
        
        return {
            "summary": summary,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "timezone": timezone,
            "location": location,
            "description": description,
            "reminders": reminders,
            "conference_data": conference_data,
            "color_id": color_id
        }
    except AttributeError as e:
        print(f"Error parsing response: {e}")
        print(f"Response content: {response}")
        return {
            "summary": "Generated Event",
            "start_datetime": "2025-08-21 10:00:00",
            "end_datetime": "2025-08-21 11:00:00",
            "timezone": "(GMT+05:00) Pakistan Standard Time",
            "location": "Online",
            "description": user_input,
            "reminders": [{"method": "popup", "minutes": 60}],
            "conference_data": True,
            "color_id": "5"
        }