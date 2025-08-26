from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from agents.linkedinAnalytics import profile_analytics_agent, analyze_post_agent
from tools.content_postingTool import content_posting_agent
from agents.linkedinContentGen import setup_llm

# main_agent.py
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from agents.linkedinContentGen import setup_llm
from agents.emailAgent import send_email

llm = setup_llm()
def main_agent(user_text: str, uploaded_file: str):
    """Main agent to handle user requests and route to appropriate tools."""

    # IMPORTANT: pass the decorated tools directly.
    tools = [
        content_posting_agent,   # name "CreateLinkedInPost"
        profile_analytics_agent, # name "ProfileAnalysis"
        analyze_post_agent,      # name "PostAnalysis"
        send_email,         # name "send_email"
    ]

    prompt = PromptTemplate.from_template(
        """You are a Personalized agent who has to assist with the following tools.

TOOLS:
- CreateLinkedInPost(topic, post_type): draft a LinkedIn post
- ProfileAnalysis(file, question): analyze uploaded analytics Excel; you MUST pass both file and a question (can be the user's request)
- PostAnalysis(content): analyze a single post; pass raw text or URL as `content`
- send_email(user_text): generate and send a professional email based on user input

Routing rules:
- If user asks to create a post → call CreateLinkedInPost(topic, post_type)
- If user provides/mentions an Excel analytics file → call ProfileAnalysis(file, question)
- If user asks to analyze a post or provides a URL → call PostAnalysis(content)
- If user just ask to write the email to someone → call send_email(user_text)
Input: {input}

Excel File Path: {uploaded_file}

If there is any file uploaded and the `input` is related to that only! then plz just use the ProfileAnalysis tool. 

If the user ask to analyze any post number to analyze its url, plz go for both Analysis tools.


{agent_scratchpad}
"""
    )

    agent = create_tool_calling_agent(llm, tools, prompt=prompt)
    exec_ = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=2,  # Limit the number of iterations
            early_stopping_method="force"  # Force stop after max_iterations
        )
    result = exec_.invoke({"input": user_text, "uploaded_file": uploaded_file})

    # Normalize result to dict
    if isinstance(result, list):
        return {"message": result}
    elif isinstance(result, dict):
        return {"message": result}
    else:
        return {"message": str(result)}