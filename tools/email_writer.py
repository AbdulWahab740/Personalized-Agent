from agents.linkedinContentGen import setup_llm
import re

def generate_email_draft(user_query: str) -> dict:
    """
    Generate a professional email draft from user input.
    Returns a dict with 'to', 'subject', and 'body' keys.
    """
    if not user_query or user_query.strip() == "":
        return {
            "to": "default@example.com",
            "subject": "No Subject", 
            "body": "Please provide the subject and any additional details (Date, Your Name, Your Company, etc.) so I can help you with the email."
        }
    
    try:
        llm = setup_llm()
        
        # Extract email from query
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", user_query)
        recipient = email_match.group(0) if email_match else "abdulwahab41467@gmail.com"
        
        prompt = f"""You are a professional email writer with extensive experience.
User input: "{user_query}"

Extract the subject from the user input and write a concise, professional email body (3-6 sentences, polite tone).

Important guidelines:
- Don't use placeholder text like [Date], [Your Name], [Your Company] 
- Only include specific details if provided by the user

Return your answer in this exact format:
To: <recipient email> if no mail is there use abdulwahab41467@gmail.com
Subject: <subject line>
Body: <email body>
"""
        
        response_obj = llm.invoke(prompt)
        response = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
        
        # Parse the response
        to_match = re.search(r"To:\s*(.*)", response)
        subject_match = re.search(r"Subject:\s*(.*)", response)
        body_match = re.search(r"Body:\s*(.*)", response, re.DOTALL)
        
        to = to_match.group(1).strip() if to_match else recipient
        subject = subject_match.group(1).strip() if subject_match else "No Subject"
        body = body_match.group(1).strip() if body_match else response.strip()
        
        return {
            "to": to,
            "subject": subject,
            "body": body
        }
        
    except Exception as e:
        print(f"Error in generate_email_draft: {e}")
        return {
            "to": "abdulwahab41467@gmail.com",
            "subject": "Error",
            "body": f"An error occurred while generating the email: {str(e)}"
        }
