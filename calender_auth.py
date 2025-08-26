from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import (
    build_resource_service,
    get_google_credentials,
)

# Can review scopes here: https://developers.google.com/calendar/api/auth
# For instance, readonly scope is https://www.googleapis.com/auth/calendar.readonly
credentials = get_google_credentials(
    token_file="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file="credentials.json",
)

api_resource = build_resource_service(credentials=credentials)
toolkit = CalendarToolkit(api_resource=api_resource)
tools = toolkit.get_tools()


print(tools)