# # frontend.py
import requests
import streamlit as st

st.title("AW Personal Automation Agent")

with st.sidebar:
    st.header("Upload an excel file if you want to analyze!")
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx",'csv'])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        # store it temporarily 
        with open(f"./uploaded_files/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File saved!")

event = ""
input_text = st.text_input("What do you want to perform? (e.g., 'Analyze a post', 'Get post content')")

if st.button("Done!!"):
    try:
        uploaded_file_path = f"./uploaded_files/{uploaded_file.name}" if uploaded_file else None
        res = requests.post(
            "http://127.0.0.1:8000/get_response",
            json={"query": input_text, "file_path":uploaded_file_path}  # Must match FastAPI's expected key
        )
        if res.status_code == 200:
            resp = res.json()
            print(resp["message"])
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
                st.success("Content Draft generated!")
            elif "compound" == resp["message"]["route"]:
                # Handle compound responses (calendar + email)
                compound_output = resp["message"]["output"]
                
                # Check if calendar was created
                if "calendar" in compound_output:
                    try:
                        st.session_state["event"] = compound_output["calendar"]["output"]["event"]
                        st.success("✅ Calendar event created!")
                    except KeyError as e:
                        st.error(f"Calendar event structure error: {e}")
                
                # Check if email was sent
                if "email" in compound_output:
                    email_result = compound_output["email"].get("output", {})
                    if email_result.get("success"):
                        st.success("✅ Email sent successfully!")
                        st.info(f"Email sent to: {email_result.get('to', 'recipient')}")
                    else:
                        st.error(f"❌ Email failed: {email_result.get('error', 'Unknown error')}")
                
                st.success("🎉 Compound action completed: Calendar event created and email sent!")
            else:

                if isinstance(resp, dict):
                    message = resp.get("message", resp)  # fallback
                else:
                    message = resp

                # Handle nested outputs
                if isinstance(message, dict) and "output" in message:
                    content = message["output"]
                else:
                    content = message
                
                st.subheader("Response")
                st.write(content)

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
        res = requests.post("http://127.0.0.1:8000/create_event", json={"event": event})
        st.write(res.json())
if "draft" in st.session_state:

    st.subheader("Review Draft Email")
    to = st.text_input("Recipient", st.session_state["draft"]["to"])
    subject = st.text_input("Subject", st.session_state["draft"]["subject"])
    body = st.text_area("Body", st.session_state["draft"]["body"], height=350)

    if st.button("Send Email"):
        draft = {"subject": subject, "body": body, "to": to}
        res = requests.post("http://127.0.0.1:8000/send_email", json={"draft": draft})
        st.write(res)

if "content" in st.session_state:
    st.subheader("Review Draft Content")
    content = st.text_area("Content", st.session_state["content"]["content"])
    if st.button("Post"):
        res = requests.post("http://127.0.0.1:8000/post_content", json={"content": content})
        st.write(res.json())