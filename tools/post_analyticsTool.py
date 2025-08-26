from langchain.tools import tool
from automation.post_content_automation import LinkedInPostContentAutomation

posts = LinkedInPostContentAutomation()

@tool
def get_linkedin_post(url: str) -> str:
    """
    Scrape the content of a LinkedIn post from the provided URL.
    
    Args:
        url (str): The URL of the LinkedIn post to scrape.
        
    Returns:
        str: The content of the LinkedIn post.
    """
    try:
        result = posts.find_content(url)
        if isinstance(result, dict):
            if "error" in result:
                return f"Error scraping post: {result['error']}"
            elif "text" in result:
                return result["text"]
            else:
                return str(result)
        return str(result)
    except Exception as e:
        return f"Error scraping post: {e}"