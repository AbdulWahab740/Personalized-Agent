from agents.linkedinContentGen import setup_llm
import re
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

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
        
        response_schemas = [
            ResponseSchema(name="to", description="Recipient email"),
            ResponseSchema(name="subject", description="Email subject line"),
            ResponseSchema(name="body", description="Email body text (3-6 sentences)")
        ]

        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()

        prompt = f"""You are a professional email writer with extensive experience.
User input: "{user_query}"

Extract the subject from the user input and write a concise, professional email body (3-6 sentences, polite tone).

Important guidelines:
- Don't use placeholder text like [Date], [Your Name], [Your Company] 
- Replace [Your Name] in body with Abdul Wahab
- You have to write an email from my side not from the one whom to send!
- Only include specific details if provided by the user
- Don't include any additional text or explanations or thinking

Return your answer in this exact format (include all three sections):
{format_instructions}
"""
        
        response = llm.invoke(prompt).content
        parsed = output_parser.parse(response)
        return parsed
        
        
    except Exception as e:
        print(f"Error in generate_email_draft: {e}")
        return {
            "to": "abdulwahab41467@gmail.com",
            "subject": "Error",
            "body": f"An error occurred while generating the email: {str(e)}"
        }
