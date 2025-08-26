from langchain.tools import tool

# load agents
from agents.linkedinContentGen import PersonalizedLinkedInContentAgent
from schemas import CreatePostInput
content_agent = PersonalizedLinkedInContentAgent()

@tool("CreateLinkedInPost", args_schema=CreatePostInput)
def content_posting_agent(topic: str, post_type: str):
    """
        Generate personalized content and post it to LinkedIn
        
        Args:
            topic: Main topic for the post
            post_type: Type of post to generate
            
        Returns:
            Dictionary with posting results
    """
    try:
            # Generate personalized content
        content_result = content_agent.generate_personalized_content(topic, post_type)
            
        if not content_result["success"]:
            return content_result
            
            # Store the post in personal agent for future reference
        post_data = {
                "content": content_result["content"],
                "topic": topic,
            }
            
        content_agent.linkedin_automation.create_post(post_data["content"])
            
        try:
                # This would integrate with your existing LinkedIn automation
                # For now, we'll just return the content
            return {
                    "success": True,
                    "content": content_result["content"],
                    "posted_to_linkedin": False,  # Set to True when integration is complete
                    "message": "Content generated and stored. LinkedIn posting integration pending.",
                    "personal_context_used": content_result["personal_context"]
                }
        except Exception as e:
                return {
                    "success": True,
                    "content": content_result["content"],
                    "posted_to_linkedin": True,
                    "message": f"Content generated but LinkedIn posting failed: {e}",
                    "personal_context_used": content_result["personal_context"]
                }
                
    except Exception as e:
            return {
                "success": False,
                "error": f"Error in create_and_post_personalized_content: {e}"
            }
