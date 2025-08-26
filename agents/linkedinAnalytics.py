# tools_bundle.py
import logging
from langchain.tools import tool, Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor, initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from typing import Dict, Any
import streamlit as st

from schemas import PostAnalysisInput, ProfileAnalysisInput, CreatePostInput
from agents.linkedinContentGen import setup_llm
from tools.post_analyticsTool import get_linkedin_post
from tools.profile_analyticsTools import (
    load_engagement, load_top_posts, load_overall_performance, load_demographics
)

llm = setup_llm()

# --- PROFILE ANALYSIS (as a tool) ---

@tool("ProfileAnalysis", args_schema=ProfileAnalysisInput,return_direct=True)
@st.cache_data(ttl=3600) 
def profile_analytics_agent(file: str, question: str = "") -> Dict[str, Any]:
    """
    Analyze LinkedIn profile analytics from an Excel export and answer the user question.
    Uses loader tools to read sheets and then reasons about them.
    """
    try:
        # expose sub-tools to an inner agent so it can choose what to load
        subtools = [
            Tool(
                name="load_engagement_data",
                func=lambda _: load_engagement(file),
                description="Loads engagement metrics & computes monthly growth for engagements & impressions."
            ),
            Tool(
                name="load_top_posts_data",
                func=lambda _: load_top_posts(file),
                description="Loads top posts data with URLs, impressions, engagements. Returns list of dictionaries with keys like 'URL', 'Post URL', 'Link', 'Impressions', 'Engagements'."
            ),
            Tool(
                name="load_overall_performance",
                func=lambda _: load_overall_performance(file),
                description="Loads overall performance totals (impressions, reach, etc.)."
            ),
            Tool(
                name="load_demographics",
                func=lambda _: load_demographics(file),
                description="Loads audience demographics."
            ),
            Tool(
                name="GetLinkedInPost",
                func=get_linkedin_post,
                description="Given a LinkedIn post URL (like https://www.linkedin.com/feed/update/urn:li:activity:XXXXXXXXX), returns the post text content. NEVER use placeholder URLs."
            ),
        ]

        prompt = PromptTemplate.from_template(
            """You are a LinkedIn profile analytics assistant.

Use the provided tools to load ONLY the data you need. Then analyze and answer the user.

CRITICAL URL EXTRACTION RULES:
1. When user asks about "best performing post" or "analyze top post":
   - FIRST call load_top_posts_data to get the top posts data
   - The data is a list of dictionaries. Look at the column names printed in debug output
   - Common URL field names: "URL", "Post URL", "Link", "Post Link", "Post", "Activity URL"
   - Extract the COMPLETE URL string from the URL field of the first post
   - The URL format should be: https://www.linkedin.com/feed/update/urn:li:activity:XXXXXXXXX
   - NEVER EVER use placeholder URLs like "https://www.linkedin.com/posts/.../*post_url*"
   - NEVER modify or truncate the URL - use it exactly as found in the data
   - THEN call GetLinkedInPost with the complete extracted URL
   - FINALLY analyze the scraped content

DEBUGGING STEPS:
1. Check debug output for column names
2. Look for URL-related columns in the first dictionary
3. Print the exact URL value before using it
4. Verify URL starts with "https://www.linkedin.com/feed/update/"

2. For general analytics:
   - Load relevant sheets (engagement, top posts, overall performance, demographics)
   - Summarize key trends and growth (MoM / weekly if present)
   - Extract top 10 posts by impressions and engagement rate

3. Always use GetLinkedInPost when you need actual post content from URLs

User request:
{input}

{agent_scratchpad}
"""
        )

        agent = create_tool_calling_agent(llm, subtools, prompt=prompt)
        exec_ = AgentExecutor(agent=agent, tools=subtools, verbose=True, handle_parsing_errors=True)
        return exec_.invoke({"input": question or "Give me a strategy from the analytics."})

    except Exception as e:
        return {"success": False, "error": f"Profile analysis failed: {e}"}


# --- POST ANALYSIS (as a tool, with nested mini-agent for scraping if URL) ---
@st.cache_data(ttl=3600) 
def analyze_post_agent(content: str) -> Dict[str, Any]:
    """
    Analyze a LinkedIn post for engagement potential.
    Accepts raw text OR a LinkedIn post URL.
    """
    try:
        # Subtool for fetching post text if a URL is given
        subtools = [
            Tool(
                name="GetLinkedInPost",
                func=get_linkedin_post,
                description="Given a LinkedIn post URL, returns the post text content."
            )
        ]

        # Explicit prompt: reference ONLY tools that exist
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template="""You are a LinkedIn content performance analyst.

You can only use the following tools:
- GetLinkedInPost: Given a LinkedIn post URL, returns the post text content.

Your task:
1. If {input} is already raw text, analyze it directly.
2. If {input} looks like a LinkedIn post URL, call **GetLinkedInPost** to fetch its text.

For your analysis include:
1) Engagement score (1-10) with a one-line reason
2) Key strengths (3-5 points)
3) Areas for improvement (3-5 points)
4) Expected reach potential (Low/Med/High) and why
5) Hashtag effectiveness (comment on density/relevance)
6) CTA quality (what to fix/add)
7) 3 concrete edits to boost engagement

End with a crisp 2-3 line summary strategy.

{agent_scratchpad}
"""
        )

        agent = create_tool_calling_agent(llm, subtools, prompt=prompt)
        exec_ = AgentExecutor(agent=agent, tools=subtools, verbose=True, handle_parsing_errors=True)

        # Run the agent
        result = exec_.invoke({"input": content})
        return {"success": True, "analysis": result}

    except Exception as e:
        return {"success": False, "error": f"Post analysis failed: {e}"}
