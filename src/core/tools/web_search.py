"""
Web search tool for IndoClaw using Tavily API.
"""

from typing import Dict, List, Optional
import os

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

from .base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """Web search tool using Tavily API."""
    
    name: str = "web_search"
    description: str = "Search the web for current information using Tavily API"
    
    def __init__(self, api_key: Optional[str] = None, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        
        # Try to get API key from parameter or environment
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = None
        
        if TAVILY_AVAILABLE and self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Tavily client: {e}")
                self.client = None
    
    def execute(self, query: str, search_depth: str = "advanced", **kwargs) -> ToolResult:
        """Execute web search."""
        if not self.client:
            return ToolResult(
                success=False,
                error="Tavily client not initialized. Please provide a valid API key."
            )
        
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=self.max_results,
                **kwargs
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0)
                })
            
            return ToolResult(
                success=True,
                content={
                    "query": query,
                    "results": results,
                    "response_time": response.get("response_time", 0)
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )
    
    def search(self, query: str) -> List[Dict]:
        """Quick search helper method."""
        result = self.execute(query)
        if result.success:
            return result.content.get("results", [])
        return []


# Example usage
if __name__ == "__main__":
    tool = WebSearchTool()
    print(tool.get_info())