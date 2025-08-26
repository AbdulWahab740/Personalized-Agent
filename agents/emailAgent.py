from automation.mail_send import gmail_send_message, extract_email
from agents.linkedinContentGen import setup_llm
from langchain.tools import tool
import re
# @tool("send_email", return_direct=True)
def send_email(user_text: str) -> dict:
    """
    Generate a professional email (subject + body) from user input and send it.
    """
    llm = setup_llm()
    try:
        recipient = extract_email(user_text)
        prompt = (
    f"""You are a professional email writer with a lot of experience.
User input: "{user_text}"
You have to extract the subject from the user input and write a concise, professional email body (3-6 sentences, polite tone) on that.

Make sure to don't put any such text [Date], [Your Name], [Your Company] etc. in the email body. Write these things if they are provided by the user.

Here's my details:
Convert [Your Name] -> Abdul Wahab
Convert [Your Linkedin Profile] -> https://www.linkedin.com/in/abwahab07/ 

Return your answer in this format:
To: <recipient email>
Subject: <subject line>
Body: <email body>
"""
)
        response_obj = llm.invoke(prompt)
        response = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
        # Simple parsing
        recipient = re.search(r"To:\s*(.*)", response).group(1).strip() if recipient is None else recipient
        subject_match = re.search(r"Subject:\s*(.*)", response)
        body_match = re.search(r"Body:\s*(.*)", response, re.DOTALL)
        subject = subject_match.group(1).strip() if subject_match else "No Subject"
        body = body_match.group(1).strip() if body_match else response.strip()
        return {"to": recipient, "subject": subject, "body": body}

    except Exception as e:
        return {"error": f"Email sending failed: {e}"}
