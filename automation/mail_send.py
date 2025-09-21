import re

def extract_email(user_text: str) -> str:
    match = re.search(r"[\w\.-]+@[\w\.-]+", user_text)
    return match.group(0) if match else "default@example.com"

# gmail_tool.py
import os, base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from langchain.tools import tool
import hashlib
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentialsss.json")
TOKEN_FILE = os.path.join(BASE_DIR, "gmailtoken.json")
sent_emails = set()  # global in-memory tracker

def gmail_send_message(subject: str, content: str, to: str):
    """Send an email using Gmail API."""
    email_key = hashlib.sha256(f"{to}-{subject}".encode()).hexdigest()

    if email_key in sent_emails:
        return {"success": False, "message": "Email already sent!"}

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        message.set_content(content)
        message["To"] = to
        message["From"] = "abdulwahab41467@gmail.com"
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        send_message = service.users().messages().send(
            userId="me", body=create_message
        ).execute()

        return {"success": True, "message": "Email sent!"}
    except HttpError as error:
        return {"success": False, "error": str(error)}


if __name__ == "__main__":
    print(gmail_send_message("Test Subject", "Test Content", "abdulwahab41467@gmail.com"))
