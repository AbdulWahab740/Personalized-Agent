#!/usr/bin/env python3
"""
LangGraph implementation of LinkedIn Analytics workflow
Provides better state management and clearer workflow visualization
"""

from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain.tools import Tool
import streamlit as st

from schemas import ProfileAnalysisInput
from agents.linkedinContentGen import setup_llm
from tools.post_analyticsTool import get_linkedin_post
from tools.profile_analyticsTools import (
    load_engagement, load_top_posts, load_overall_performance, load_demographics
)

# State definition
class AnalyticsState(TypedDict):
    user_query: str
    file_path: str
    analysis_type: str
    loaded_data: Dict[str, Any]
    extracted_url: str
    scraped_content: str
    analysis_result: str
    error: str

class LinkedInAnalyticsGraph:
    def __init__(self):
        self.llm = setup_llm()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AnalyticsState)
        
        # Add nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("load_data", self._load_data_node)
        workflow.add_node("extract_url", self._extract_url_node)
        workflow.add_node("scrape_content", self._scrape_content_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("format_response", self._format_response_node)
        
        # Define edges
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "post_analysis": "load_data",
                "general_analytics": "load_data",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "load_data",
            self._data_loaded_decision,
            {
                "extract_url": "extract_url",
                "analyze": "analyze",
                "error": END
            }
        )
        
        workflow.add_edge("extract_url", "scrape_content")
        workflow.add_edge("scrape_content", "analyze")
        workflow.add_edge("analyze", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _router_node(self, state: AnalyticsState) -> AnalyticsState:
        """Determine the type of analysis needed"""
        query = state["user_query"].lower()
        
        if any(phrase in query for phrase in ["analyze best", "analyze top post", "analyze post", "top post content", "url", "top post","performing post", "best performing post" ]):
            analysis_type = "post_analysis"
        else:
            analysis_type = "general_analytics"
        
        return {
            **state,
            "analysis_type": analysis_type
        }
    
    def _load_data_node(self, state: AnalyticsState) -> AnalyticsState:
        """Load appropriate data based on analysis type"""
        try:
            file_path = state["file_path"]
            analysis_type = state["analysis_type"]
            loaded_data = {}
            
            print(f"DEBUG: Loading data from file: {file_path}")
            print(f"DEBUG: Analysis type: {analysis_type}")
            
            if analysis_type == "post_analysis":
                # Load top posts data for post analysis
                top_posts_data = load_top_posts(file_path)
                loaded_data["top_posts"] = top_posts_data
                print(f"DEBUG: Loaded top posts data type: {type(top_posts_data)}")
                print(f"DEBUG: Loaded top posts data: {top_posts_data[:1] if isinstance(top_posts_data, list) else top_posts_data}")
                
            elif analysis_type == "general_analytics":
                # Load all relevant data for general analytics
                loaded_data["engagement"] = load_engagement(file_path)
                loaded_data["top_posts"] = load_top_posts(file_path)
                loaded_data["overall"] = load_overall_performance(file_path)
                loaded_data["demographics"] = load_demographics(file_path)
            
            return {
                **state,
                "loaded_data": loaded_data
            }
            
        except Exception as e:
            print(f"DEBUG: Error loading data: {e}")
            return {
                **state,
                "error": f"Failed to load data: {str(e)}"
            }
    
    def _extract_url_node(self, state: AnalyticsState) -> AnalyticsState:
        """Extract URL from top posts data"""
        try:
            top_posts_data = state["loaded_data"].get("top_posts", [])
            print(f"DEBUG: URL extraction - top_posts_data type: {type(top_posts_data)}")
            print(f"DEBUG: URL extraction - top_posts_data: {top_posts_data}")
            
            if not top_posts_data or (isinstance(top_posts_data, dict) and "error" in top_posts_data):
                print(f"DEBUG: No valid top posts data for URL extraction")
                return {
                    **state,
                    "error": "No top posts data available for URL extraction"
                }
            
            # Get the first (best performing) post
            first_post = top_posts_data[0] if isinstance(top_posts_data, list) and len(top_posts_data) > 0 else {}
            print(f"DEBUG: First post data keys: {list(first_post.keys()) if first_post else 'No keys'}")
            print(f"DEBUG: First post data: {first_post}")
            
            # Try different possible URL field names
            url_fields = ["Post URL", "URL", "Link", "Post Link", "Post", "Activity URL", "url", "link", "post_url"]
            extracted_url = None
            
            for field in url_fields:
                if field in first_post and first_post[field] and str(first_post[field]).strip():
                    extracted_url = str(first_post[field]).strip()
                    print(f"DEBUG: Found URL in field '{field}': {extracted_url}")
                    break
            
            if not extracted_url:
                available_fields = list(first_post.keys()) if first_post else []
                print(f"DEBUG: No URL found. Available fields: {available_fields}")
                return {
                    **state,
                    "error": f"No URL field found. Available fields: {available_fields}"
                }
            
            # Validate URL format
            if not extracted_url.startswith("https://www.linkedin.com/"):
                print(f"DEBUG: Invalid URL format: {extracted_url}")
                return {
                    **state,
                    "error": f"Invalid LinkedIn URL format: {extracted_url}"
                }
            
            print(f"DEBUG: Successfully extracted URL: {extracted_url}")
            return {
                **state,
                "extracted_url": extracted_url
            }
            
        except Exception as e:
            print(f"DEBUG: Exception in URL extraction: {e}")
            return {
                **state,
                "error": f"Failed to extract URL: {str(e)}"
            }
    
    def _scrape_content_node(self, state: AnalyticsState) -> AnalyticsState:
        """Scrape content from the extracted URL"""
        try:
            url = state["extracted_url"]
            print(f"DEBUG: Scraping content from URL: {url}")
            
            scraped_content = get_linkedin_post(url)
            
            if "Error scraping post" in scraped_content:
                return {
                    **state,
                    "error": f"Failed to scrape content: {scraped_content}"
                }
            
            return {
                **state,
                "scraped_content": scraped_content
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Failed to scrape content: {str(e)}"
            }
    
    def _analyze_node(self, state: AnalyticsState) -> AnalyticsState:
        """Perform analysis based on the loaded data and scraped content"""
        try:
            analysis_type = state["analysis_type"]
            
            if analysis_type == "post_analysis":
                # Analyze the scraped post content
                content = state.get("scraped_content", "")
                if not content:
                    return {
                        **state,
                        "error": "No content available for analysis"
                    }
                
                prompt = f"""Analyze this LinkedIn post for engagement potential:

Content: {content}

Provide analysis including:
1. Engagement score (1-10) with reasoning
2. Key strengths (3-5 points)
3. Areas for improvement (3-5 points)
4. Expected reach potential (Low/Med/High) and why
5. Hashtag effectiveness
6. CTA quality
7. 3 concrete edits to boost engagement
8. 2-3 line summary strategy
"""
                
            else:
                # General analytics analysis
                loaded_data = state["loaded_data"]
                prompt = f"""Analyze this LinkedIn profile analytics data:

Data: {loaded_data}

Provide insights including:
1. Key performance trends
2. Top performing content patterns
3. Audience engagement insights
4. Growth opportunities
5. Content strategy recommendations
"""
            
            response = self.llm.invoke(prompt)
            analysis_result = response.content if hasattr(response, 'content') else str(response)
            
            return {
                **state,
                "analysis_result": analysis_result
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Failed to analyze: {str(e)}"
            }
    
    def _format_response_node(self, state: AnalyticsState) -> AnalyticsState:
        """Format the final response"""
        analysis_result = state.get("analysis_result", "")
        
        if state["analysis_type"] == "post_analysis":
            url = state.get("extracted_url", "")
            formatted_response = f"""# LinkedIn Post Analysis

**Analyzed Post URL:** {url}

## Analysis Results:
{analysis_result}
"""
        else:
            formatted_response = f"""# LinkedIn Analytics Report

{analysis_result}
"""
        
        return {
            **state,
            "analysis_result": formatted_response
        }
    
    def _route_decision(self, state: AnalyticsState) -> str:
        """Decide routing based on analysis type"""
        if state.get("error"):
            return "error"
        return state.get("analysis_type", "general_analytics")
    
    def _data_loaded_decision(self, state: AnalyticsState) -> str:
        """Decide next step after loading data"""
        if state.get("error"):
            return "error"
        
        if state["analysis_type"] == "post_analysis":
            return "extract_url"
        else:
            return "analyze"
    
    def analyze(self, file_path: str, query: str) -> Dict[str, Any]:
        """Run the analytics workflow"""
        try:
            initial_state = AnalyticsState(
                user_query=query,
                file_path=file_path,
                analysis_type="",
                loaded_data={},
                extracted_url="",
                scraped_content="",
                analysis_result="",
                error=""
            )
            result = self.graph.invoke(initial_state)
            if result.get("error"):
                return {"success": False, "error": result["error"]}
            
            return {
                "success": True,
                "analysis": result["analysis_result"],
                "analysis_type": result["analysis_type"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Workflow failed: {str(e)}"}

# Tool wrapper for compatibility
@st.cache_data(ttl=3600)
def profile_analytics_agent(file: str, question: str = "") -> Dict[str, Any]:
    """
    LangGraph-based LinkedIn profile analytics agent
    """
    try:
        graph_agent = LinkedInAnalyticsGraph()
        return graph_agent.analyze(file, question)
    except Exception as e:
        return {"success": False, "error": f"Graph analysis failed: {e}"}
