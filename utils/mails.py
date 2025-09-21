import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# SCOPES: add what you need
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar"
]

def get_tokens():
    creds = None
    if os.path.exists("gmailtoken.json"):
        creds = Credentials.from_authorized_user_file("gmailtoken.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        with open("gmailtoken.json", "w") as token:
            token.write(creds.to_json())

    print("✅ Tokens saved to gmailtoken.json")
    return creds

if __name__ == "__main__":
    creds = get_tokens()
    print("Access Token:", creds.token)
    print("Refresh Token:", creds.refresh_token)
