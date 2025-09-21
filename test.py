# from agents.linkedinContentGen import setup_llm
# from langchain_google_community.calendar.create_event import CalendarCreateEvent
# from dotenv import load_dotenv
# from utils.calender_event import generate_event

# load_dotenv()

# def calender_event(user_input: str):
#     event = generate_event(user_input)
#     print(event)
#     tool = CalendarCreateEvent()
#     tool.invoke(
#         {
#             "summary": event["summary"],
#             "start_datetime": event["start_datetime"],
#             "end_datetime": event["end_datetime"],
#             "timezone": event["timezone"],
#             "location": event["location"],
#             "description": event["description"],
#             "reminders": event["reminders"],
#             "conference_data": event["conference_data"],
#             "color_id": event["color_id"],
#         }
#     )
#     return {"success": True, "message": "Event created successfully"}

# if __name__ == "__main__":
#     calender_event("Meeting with John Doe")
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# SCOPES: add what you need
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTOMATION_DIR = os.path.join(BASE_DIR, "automation")
CREDENTIALS_FILE = os.path.join(AUTOMATION_DIR, "credentialsss.json")
TOKEN_FILE = os.path.join(AUTOMATION_DIR, "gmailtoken.json")

def get_tokens():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    print("✅ Tokens saved to", TOKEN_FILE)
    return creds

if __name__ == "__main__":
    creds = get_tokens()
    print("Access Token:", creds.token)
    print("Refresh Token:", creds.refresh_token)
