from langchain_google_community.calendar.get_calendars_info import GetCalendarsInfo

tool = GetCalendarsInfo(name="Abdulwahab")
response = tool.invoke({})


print(response)