"""
DuckDuckGo web search tool for IndoClaw.
Provides web search capabilities using DuckDuckGo.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import logging

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.warning("ddgs package not installed")
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        logging.warning("duckduckgo_search package also not installed")

from .base import BaseTool, ToolResult


@dataclass
class SearchResult:
    """Represents a search result."""
    title: str
    url: str
    snippet: str
    source: str = "duckduckgo"


class DuckDuckGoSearchTool(BaseTool):
    """Search the web using DuckDuckGo."""
    
    name = "duckduckgo_search"
    description = "Search the web using DuckDuckGo. Input should be a search query."
    
    def __init__(self, max_results: int = 10):
        super().__init__()
        self.max_results = max_results
        self.enabled = DDGS_AVAILABLE
        self._ddgs = None  # Reuse DDGS instance for efficiency
    
    def _get_ddgs(self):
        """Get or create DDGS instance."""
        if self._ddgs is None:
            self._ddgs = DDGS()
        return self._ddgs
    
    def execute(self, query: str) -> ToolResult:
        """Execute a DuckDuckGo search."""
        if not DDGS_AVAILABLE:
            return ToolResult(
                success=False,
                error="duckduckgo-search package not installed. Run: pip install duckduckgo-search"
            )
        
        try:
            ddgs = self._get_ddgs()
            results = list(ddgs.text(query, max_results=self.max_results))
            
            if not results:
                return ToolResult(
                    success=True,
                    content={
                        "results": [],
                        "summary": "No results found for your query."
                    }
                )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo"
                })
            
            return ToolResult(
                success=True,
                content={
                    "results": formatted_results,
                    "summary": f"Found {len(formatted_results)} results for '{query}'"
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"DuckDuckGo search failed: {str(e)}"
            )
    
    def close(self):
        """Close the DDGS session."""
        if self._ddgs is not None:
            try:
                self._ddgs.__exit__(None, None, None)
            except:
                pass
            self._ddgs = None
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        if not results:
            return "No results found."
        
        output = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("snippet", "")
            
            output.append(f"{i}. {title}")
            output.append(f"   URL: {url}")
            output.append(f"   Summary: {snippet[:200]}..." if len(snippet) > 200 else f"   Summary: {snippet}")
            output.append("")
        
        return "\n".join(output)


# Create default instance
duckduckgo_search_tool = DuckDuckGoSearchTool()