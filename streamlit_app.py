# # # frontend.py
import requests
import streamlit as st

st.set_page_config(page_title="AW Personal Agent", page_icon="🤖", layout="wide")

ROUTE_KEYS = {
    "email": ["email_to", "email_subject", "email_body"],
    "content": ["content_text"],
    "calender": [
        "calendar_summary", "calendar_start", "calendar_end",
        "calendar_timezone", "calendar_location", "calendar_description",
        "calendar_reminders", "calendar_conf", "calendar_color_id"
    ],
    "analysis": ["analysis"]
}
# ---- HEADER ----
st.markdown(
    """
    <h1 style='text-align: center; color: #257180;'>🤖 AW Personal Agent</h1>
    <p style='text-align: center; color: gray;'>
        My AI-powered assistant for content, email, and calender scheduling
    </p>
    <hr>
    """,
    unsafe_allow_html=True,
)

# ---- SIDEBAR ----
with st.sidebar:
    st.header("📂 Upload Analytics File")
    uploaded_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])

    if uploaded_file:
        with open(f"./uploaded_files/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {uploaded_file.name} saved!")

# ---- MAIN INPUT ----
# st.subheader(/"")
input_text = st.chat_input(
    "Try things like: 'Post content', 'Analyze a post', 'Send an email', 'Create a calendar event'",
    # placeholder="Type your command here..."
)
def reset_state():
    """Clear session_state for given keys."""
    # print(st.session_state)
    for key in st.session_state:
        del st.session_state[key]


if "last_route" not in st.session_state:
    st.session_state.last_route = None


if input_text:
    try:
        uploaded_file_path = f"./uploaded_files/{uploaded_file.name}" if uploaded_file else None
        res = requests.post(
            "http://127.0.0.1:8000/get_response",
            json={"query": input_text, "file_path":uploaded_file_path}  # Must match FastAPI's expected key
        )
        if res.status_code == 200:
            resp = res.json()
            if resp["message"]["route"] != st.session_state.last_route:
                reset_state()  # <-- CLEAR OLD KEYS ONLY WHEN ROUTE CHANGES
                st.session_state.last_route = resp["message"]["route"]
            # print(resp["message"])
            # Check if this is an email response with draft
            if "email" == resp["message"]["route"]:
                st.session_state["draft"] = resp["message"]["output"]["draft"]
                st.success("Draft generated!")
            elif "calender" == resp["message"]["route"]:
                try:
                    st.session_state["event"] = resp["message"]["output"]["output"]["event"]
                    st.success("Event generated!")
                except KeyError as e:
                    st.error(f"Calendar event structure error: {e}")
                    st.write("Full response:", resp["message"])
            elif "content" == resp["message"]["route"]:
                st.session_state["content"] = resp["message"]["output"]["content"]
                print(st.session_state["content"])
                st.success("Content Draft generated!")
            elif "compound" == resp["message"]["route"]:
                # Handle compound responses (calendar + email)
                compound_output = resp["message"]["output"]
                st.session_state.compound = True
                # Check if calendar was created
                if "calendar" in compound_output and compound_output["calendar"]:
                    try:
                        st.session_state["event"] = compound_output["calendar"].get("output", {}).get("event", {})
                    except Exception as e:
                        st.error(f"Error processing calendar event: {e}")
                st.write(compound_output)
                st.session_state.comp_draft = compound_output['draft']
                # Check if email was sent
                if compound_output["draft"]:
                        st.subheader("Review Draft Email")
                        st.session_state.to_comp = st.text_input("Recipient", compound_output["draft"]["to"], key="to_comp")
                        st.session_state.subject_comp = st.text_input("Subject", compound_output["draft"]["subject"], key="subject_comp")
                        st.session_state.body_comp = st.text_area("Body", compound_output["draft"]["body"], height=350, key="body_comp")
            else:
                # Handle nested outputs
                if isinstance(resp, dict) and "message" in resp and "output" in resp["message"]:
                    content = resp["message"]["output"]
                else:
                    content = resp
                
                st.subheader("Response")
                if "analysis" in content:
                    st.markdown(content["analysis"])
                else:
                    st.write("No analysis found in response.")
                    st.json(content)  # Debug full content


        else:
            st.error(f"Error: {res.status_code} - {res.text}")

    except Exception as e:
        st.error(f"Request failed: {e}")

if "event" in st.session_state:
    st.subheader("Review Event")
    summary = st.text_input("Summary", st.session_state["event"]["summary"])
    start_datetime = st.text_input("Start DateTime", st.session_state["event"]["start_datetime"])
    end_datetime = st.text_input("End DateTime", st.session_state["event"]["end_datetime"])
    timezone = st.text_input("Timezone", st.session_state["event"]["timezone"])
    location = st.text_input("Location", st.session_state["event"]["location"])
    description = st.text_area("Description", st.session_state["event"]["description"], height=200)
    reminders = st.text_input("Reminders", st.session_state["event"]["reminders"])
    conference_data = st.text_input("Conference Data", st.session_state["event"]["conference_data"])
    color_id = st.text_input("Color ID", st.session_state["event"]["color_id"])
    if st.button("Create Event"):
        # Convert string fields back to proper types
        import ast
        try:
            reminders_list = ast.literal_eval(reminders) if isinstance(reminders, str) else reminders
        except:
            reminders_list = [{"method": "popup", "minutes": 60}]
        
        conference_data_bool = conference_data.lower() == 'true' if isinstance(conference_data, str) else conference_data
        
        event = {
            "summary": summary, 
            "start_datetime": start_datetime, 
            "end_datetime": end_datetime, 
            "timezone": timezone, 
            "location": location, 
            "description": description, 
            "reminders": reminders_list, 
            "conference_data": conference_data_bool, 
            "color_id": color_id
        }
        requests.post("http://127.0.0.1:8000/create_event", json={"event": event})
        if st.session_state.compound:
            edited_draft = {
                "to": st.session_state.to_comp,
                "subject": st.session_state.subject_comp,
                "body": st.session_state.body_comp
            }
            requests.post("http://127.0.0.1:8000/send_email", json={"draft": edited_draft})
            st.success("✓ Email sent successfully!")
if "draft" in st.session_state:

    st.subheader("Review Draft Email")
    to = st.text_input("Recipient", st.session_state["draft"]["to"],key="to")
    subject = st.text_input("Subject", st.session_state["draft"]["subject"],key="subject")
    body = st.text_area("Body", st.session_state["draft"]["body"], height=350,key="body")

    if st.button("Send Email"):
        draft = {"subject": subject, "body": body, "to": to}
        requests.post("http://127.0.0.1:8000/send_email", json={"draft": draft})
        st.success("✓ Email sent successfully!")

if "content" in st.session_state:
    st.subheader("Review Draft Content")
    
    # Convert to string safely
    current_content = st.session_state.get("content", "")
    
    content = st.text_area("Content", current_content["content"]["analysis"], key="content_area")
    
    if st.button("Post"):
        requests.post("http://127.0.0.1:8000/post_content", json={"content": content})
        st.success("✓ Content posted successfully!")

# # frontend.py
# import requests
# import streamlit as st
# from datetime import datetime

# st.set_page_config(page_title="AW Personal Agent", page_icon="🤖", layout="wide")

# ROUTE_KEYS = {
#     "email": ["email_to", "email_subject", "email_body"],
#     "content": ["content_text"],
#     "calender": [
#         "calendar_summary", "calendar_start", "calendar_end",
#         "calendar_timezone", "calendar_location", "calendar_description",
#         "calendar_reminders", "calendar_conf", "calendar_color_id"
#     ],
#     "analysis": ["analysis"]
# }
# # ---- HEADER ----
# st.markdown(
#     """
#     <h1 style='text-align: center; color: #257180;'>🤖 AW Personal Agent</h1>
#     <p style='text-align: center; color: gray;'>
#         My AI-powered assistant for content, email, and calender scheduling
#     </p>
#     <hr>
#     """,
#     unsafe_allow_html=True,
# )

# # ---- SIDEBAR ----
# with st.sidebar:
#     st.header("📂 Upload Analytics File")
#     uploaded_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])

#     if uploaded_file:
#         with open(f"./uploaded_files/{uploaded_file.name}", "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         st.success(f"✅ {uploaded_file.name} saved!")

# # ---- MAIN INPUT ----
# # st.subheader(/"")
# input_text = st.chat_input(
#     "Try things like: 'Post content', 'Analyze a post', 'Send an email', 'Create a calendar event'",
#     # placeholder="Type your command here..."
# )
# def reset_state():
#     """Clear session_state for given keys."""
#     # print(st.session_state)
#     for key in st.session_state:
#         del st.session_state[key]

# def submitted():
#     st.session_state.submitted = True
# def reset():
#     st.session_state.submitted = False


# # ---- RESPONSE HANDLING ----
# if input_text:
#     try:
#         uploaded_file_path = f"./uploaded_files/{uploaded_file.name}" if uploaded_file else None
#         res = requests.post(
#             "http://127.0.0.1:8000/get_response",
#             json={"query": input_text, "file_path": uploaded_file_path}
#         )
#         if res.status_code == 200:
#             resp = res.json()
#             route = resp["message"].get("route", "")
#             output = resp["message"].get("output", {})
#             print(resp)

#             # ---- EMAIL ----
#             if route == "email":
#                 st.success("📧 Draft Email Generated!")
#                 st.subheader("Review & Edit Email")
#                 with st.form("email_form"):
#                     to = st.text_input("Recipient",
#                                     value=st.session_state.get("email_to", output["draft"]["to"]),
#                                     key="email_to")
#                     subject = st.text_input("Subject",
#                                             value=st.session_state.get("email_subject", output["draft"]["subject"]),
#                                             key="email_subject")
#                     body = st.text_area("Body",
#                                         value=st.session_state.get("email_body", output["draft"]["body"]),
#                                         height=250,
#                                         key="email_body")
#                     st.form_submit_button("📨 Send Email",on_click=submitted)
#                 if "submitted" in st.session_state:
#                     if st.session_state.submitted == True:
#                         draft = {
#                             "to": st.session_state.email_to,
#                             "subject": st.session_state.email_subject,
#                             "body": st.session_state.email_body
#                         }
#                         requests.post("http://127.0.0.1:8000/send_email", json={"draft": draft})
#                         st.success("✅ Email sent successfully!")
#                         reset()
#             # ---- CALENDAR ----
#             elif route == "calender":
                
#                 st.success("📅 Event Draft Generated!")
#                 event = output["output"]["event"]

#                 defaults = {
#                     "calendar_summary": event["summary"],
#                     "calendar_start": event["start_datetime"],
#                     "calendar_end": event["end_datetime"],
#                     "calendar_timezone": event["timezone"],
#                     "calendar_location": event["location"],
#                     "calendar_description": event["description"],
#                     "calendar_reminders": str(event["reminders"]),
#                     "calendar_conf": str(event["conference_data"]),
#                     "calendar_color_id": event["color_id"]
#                 }
#                 for key, value in defaults.items():
#                     if key not in st.session_state:
#                         st.session_state[key] = value

#                 with st.form("event_form"):
#                     summary = st.text_input("Summary", key="calendar_summary")
#                     start_datetime = st.text_input("Start", key="calendar_start")
#                     end_datetime = st.text_input("End", key="calendar_end")
#                     timezone = st.text_input("Timezone", key="calendar_timezone")
#                     location = st.text_input("Location", key="calendar_location")
#                     description = st.text_area("Description", key="calendar_description", height=150)
#                     reminders = st.text_input("Reminders", key="calendar_reminders")
#                     conf = st.text_input("Conference Data", key="calendar_conf")
#                     color_id = st.text_input("Color ID", key="calendar_color_id")
                    
#                     # print(event_data)
#                     st.form_submit_button("📌 Create Event",on_click=submitted)
#                 if "submitted" in st.session_state:
#                     if st.session_state.submitted == True:
#                         print("Creating event")
#                         event_data = {
#                         "summary": summary, 
#                         "start_datetime": start_datetime, 
#                         "end_datetime": end_datetime, 
#                         "timezone": timezone, 
#                         "location": location, 
#                         "description": description, 
#                         "reminders": reminders, 
#                         "conference_data": conf, 
#                         "color_id": color_id
#                     }
#                         requests.post("http://127.0.0.1:8000/create_event", json={"event": event_data})
#                         st.success("✅ Event created successfully!")
#                         reset()

#             # ---- CONTENT ----
#             elif route == "content":
#                 st.success("📝 Content Draft Generated!")
#                 content_text = output["content"]["content"]["analysis"]
#                 with st.form("content_form"):
#                     content = st.text_area(
#                         "Content",
#                         value=st.session_state.get("content_text", content_text),
#                         height=250,
#                         key="content_text"
#                     )
#                     st.form_submit_button("🚀 Post Content",on_click=submitted)
#                 if "submitted" in st.session_state:
#                     if st.session_state.submitted == True:
#                         requests.post("http://127.0.0.1:8000/post_content", json={"content": st.session_state.content_text})
#                         st.success("✅ Content posted successfully!")
#                         reset()
#             else:
#                 # Handle nested outputs
#                 if isinstance(resp, dict) and "message" in resp and "output" in resp["message"]:
#                     content = resp["message"]["output"]
#                 else:
#                     content = resp
#                 st.subheader("Response")
#                 if "analysis" in content:
#                     st.session_state.analysis = content["analysis"]
#                     st.markdown(st.session_state.analysis)
#                 else:
#                     st.write("No analysis found in response.")
#                     st.json(content)  # Debug full content

#         else:
#             st.error(f"Error: {res.status_code} - {res.text}")

#     except Exception as e:
#         st.error(f"❌ Request failed: {e}")
