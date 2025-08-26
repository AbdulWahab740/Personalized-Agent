#!/usr/bin/env python3
"""
Integration script showing how to connect Personal Information Agent 
with LinkedIn automation for personalized content generation using LLM
"""
import streamlit as st
from utils.personal_info import PersonalInfo
from automation.linkedin_content_automation import LinkedInContentAutomation
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

from dotenv import load_dotenv
load_dotenv()
import json
import os

_LLM_INSTANCE = None

def setup_llm():
    """Set up the LLM for the agent with error handling"""
    global _LLM_INSTANCE
    if _LLM_INSTANCE is None:
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            _LLM_INSTANCE = ChatGroq(
                model="llama3-8b-8192",
                temperature=0.7,
                max_tokens=3000,
                api_key=api_key,
            )
            print("✅ LLM setup successful")
        except Exception as e:
            print(f"❌ Error setting up LLM: {e}")
            # Return a mock LLM that returns error messages
            _LLM_INSTANCE = MockLLM()
    return _LLM_INSTANCE

class MockLLM:
    """Mock LLM for when the real LLM fails to initialize"""
    def invoke(self, prompt):
        class MockResponse:
            content = "Error: Unable to connect to LLM service. Please check your internet connection and API key."
        return MockResponse()

# Global LLM instance
llm = setup_llm()

class PersonalizedLinkedInContentAgent:
    """
    Combines Personal Information Agent with LinkedIn automation
    to create personalized, context-aware LinkedIn posts using LLM
    """
    
    def __init__(self, llm_instance=None):
        self.personal_agent = PersonalInfo()
        self.personal_agent._load_profile_from_json()
        self.personal_profile = self.personal_agent.personal_profile 
        self.linkedin_automation = LinkedInContentAutomation()
        self.llm = llm_instance if llm_instance else llm
        
    def _get_concise_personal_context(self, topic: str) -> str:
        """Get a concise personal context for the given topic"""
        try:
            # Get a brief summary instead of full profile
            if hasattr(self.personal_agent, 'get_personal_summary'):
                summary = self.personal_agent.get_personal_summary()
                # Extract key points relevant to the topic
                key_points = []
                if topic.lower() in summary.lower():
                    key_points.append(f"Topic relevant: {topic}")
                if "Skills" in summary:
                    skills_section = summary.split("Skills")[1].split("\n\n")[0] if "Skills" in summary else ""
                    key_points.append(f"Skills: {skills_section[:200]}...")
                if "Projects" in summary:
                    projects_section = summary.split("Projects")[1].split("\n\n")[0] if "Projects" in summary else ""
                    key_points.append(f"Projects: {projects_section[:200]}...")
                
                return "\n".join(key_points) if key_points else "Professional with relevant experience in the field."
            else:
                return "Professional with relevant experience in the field."
        except Exception as e:
            print(f"Error getting concise context: {e}")
            return "Professional with relevant experience in the field."

    def generate_personalized_content(self, topic: str) -> dict:
        """
        Generate personalized LinkedIn content based on stored personal information using LLM
        
        Args:
            topic: Main topic for the post
            
        Returns:
            Dictionary containing personalized content and metadata
        """
        try:
            # Get relevant personal information
            relevant_info = self.personal_agent.search_personal_info(topic)
            
            if not relevant_info:
                return {
                    "success": False,
                    "error": f"No relevant information found for topic: {topic}"
                }
            
            # Get writing style guidance
            writing_style = self.personal_agent.personal_profile.get("writing_style_notes", "Professional and engaging")
            
            # Check if context is too long and use concise version if needed
            context_length = sum(len(info.page_content) for info in relevant_info)
            if context_length > 3000:  # If context is too long
                print(f"⚠️ Context too long ({context_length} chars). Using concise version...")
                relevant_info = [Document(
                    page_content=self._get_concise_personal_context(topic),
                    metadata={"type": "concise_context"}
                )]
            
            # Generate personalized content using LLM
            content = self._generate_llm_post(topic, relevant_info, writing_style)
            
            return {
                "success": True,
                "content": content,
                "topic": topic,
                "personal_context": len(relevant_info),
                "writing_style_applied": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating personalized content: {e}"
            }
    
    def _truncate_context(self, context_info: str, max_chars: int = 1500) -> str:
        """Truncate context to prevent token limit exceeded errors"""
        if len(context_info) <= max_chars:
            return context_info
        
        # Truncate and add ellipsis
        truncated = context_info[:max_chars].rsplit(' ', 1)[0] + "..."
        print(f"⚠️ Context truncated from {len(context_info)} to {len(truncated)} characters to prevent token limit exceeded")
        return truncated

    def _generate_llm_post(self, topic: str, relevant_info: list, writing_style: str) -> str:
        """Generate LinkedIn post content using LLM with PromptTemplate"""
        
        # Create context from relevant personal information
        context_info = "\n".join([info.page_content for info in relevant_info])
        
        # Truncate context to prevent token limit exceeded
        context_info = self._truncate_context(context_info, max_chars=1500)
        
        # Truncate writing style if too long
        writing_style = self._truncate_context(writing_style, max_chars=500)
        
        # Define post type specific prompt templates
        post_template = PromptTemplate(
                input_variables=["topic", "context_info", "writing_style"],
                template="""You are a professional LinkedIn content creator. Create an engaging LinkedIn post about {topic}.

You have to idenify the post_type based on the topic .. it could be either these 
[acheivements, insights, question, story, general]

Use this personal context information to make it authentic and personalized:
{context_info}

Note: You don't need to exagerate or write wrong information. Tell only what I did!
Writing style guidance: {writing_style} 

Requirements:
- Start with an engaging hook
- Never use emoji!!
- Include specific details from the personal context if it requires
- Make it inspiring, engaging, shareable and knowledgeful
- End with a question to encourage engagement
- Add 3-5 relevant hashtags
- Keep it under 500 words
- Use bullet points or short paragraphs for readability
- Make it sound like a real person sharing their experience with a touch of humor
- Don't miss to ask the Follow-up or P.S. relevant to the topic (Don't write like : **Follow-up** but can write **P.S.**) just keep it engaging
- Don't write like `Here's is the linkedin post for you` just start the content about topic
Generate a compelling LinkedIn post:
"""
            ),
        
        try:
            
            chain = post_template | self.llm 
            # Generate content using LLM
            response = chain.invoke({"topic": topic, "context_info": context_info, "writing_style": writing_style})
            generated_content = response.content.strip()
            
            # Clean up the response if needed
            if generated_content.startswith("```"):
                generated_content = generated_content.split("```")[1]
            if generated_content.endswith("```"):
                generated_content = generated_content.rsplit("```", 1)[0]
            print(f"Generated content: {generated_content}")
            return generated_content
            
        except Exception as e:
            # Check if it's a token limit error
            if "Request too large" in str(e) or "tokens per minute" in str(e):
                print(f"🔄 Token limit exceeded. Using fallback concise prompt...")
                return self._generate_fallback_post(topic)
            else:
                # Fallback to template-based generation if LLM fails
                print(f"LLM generation failed: {e}. Falling back to template-based generation.")
                return self._generate_template_post(topic)

    def _generate_fallback_post(self, topic: str) -> str:
        """Generates a more concise post when token limit is exceeded."""
        print("Using fallback concise prompt due to token limit exceeded.")
        # Define a more concise prompt template
        concise_template = PromptTemplate(
            input_variables=["topic"],
            template="""You are a professional LinkedIn content creator. Create a concise LinkedIn post about {topic}.

Requirements:
- Start with an engaging hook
- Never use emoji!!
- Keep it under 200 words
- Make it sound like a real person sharing their thoughts
- Add 3-5 relevant hashtags

Generate a compelling LinkedIn post:"""
        )
        try:
            formatted_prompt = concise_template.format(topic=topic)
            response = self.llm.invoke(formatted_prompt)
            generated_content = response.content.strip()
            
            # Clean up the response if needed
            if generated_content.startswith("```"):
                generated_content = generated_content.split("```")[1]
            if generated_content.endswith("```"):
                generated_content = generated_content.rsplit("```", 1)[0]
            return generated_content
        except Exception as e:
            print(f"Fallback post generation failed: {e}")
            return "Error generating fallback post."

    def _generate_template_post(self, topic: str) -> str:
        """Generates a post using the general template when LLM fails."""
        print("Falling back to general template post generation.")
        # Define the general prompt template
        general_template = PromptTemplate(
            input_variables=["topic"],
            template="""You are a professional LinkedIn content creator. Create an engaging LinkedIn post about {topic} that shares thoughts and encourages discussion.

Requirements:
- Start with an engaging hook
- Never use emoji!!
- Share thoughts and perspectives on {topic}
- Include relevant details from the personal context
- Make it interesting and shareable
- End with a question or call to action
- Add 3-5 relevant hashtags
- Keep it under 300 words
- Make it sound like a real person sharing their thoughts

Generate a compelling LinkedIn post:"""
        )
        try:
            formatted_prompt = general_template.format(topic=topic)
            response = self.llm.invoke(formatted_prompt)
            generated_content = response.content.strip()
            if generated_content.startswith("```"):
                generated_content = generated_content.split("```")[1]
            if generated_content.endswith("```"):
                generated_content = generated_content.rsplit("```", 1)[0]
            return generated_content
        except Exception as e:
            print(f"General template post generation failed: {e}")
            return "Error generating general template post."

    