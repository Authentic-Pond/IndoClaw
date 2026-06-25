"""
Researcher Agent for IndoClaw.
Specialized in gathering and analyzing information from various sources.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .base import BaseAgent
from ..core.tools.base import BaseTool
from ..core.tools import _tool_registry
from ..core.memory.short_term import ShortTermMemory
from ..config.settings import settings


@dataclass
class ResearchResult:
    """Result of a research task."""
    query: str
    findings: List[Dict[str, str]]
    sources: List[str]
    summary: str
    confidence: float


class ResearcherAgent(BaseAgent):
    """
    Researcher agent specialized in information gathering and analysis.
    Uses the tool registry for pluggable tool access.
    """

    name: str = "Researcher"
    description: str = "Specializes in gathering and analyzing information"

    def __init__(
        self,
        api_key: Optional[str] = None,
        verbose: bool = False
    ):
        # Get model configuration
        model_name = settings.llm.model_name
        temperature = settings.llm.temperature
        api_key = api_key or settings.llm.api_key
        base_url = settings.llm.base_url if settings.llm.ollama_enabled else settings.llm.api_base

        # Check if Ollama is being used
        self.using_ollama = settings.llm.ollama_enabled

        super().__init__(
            name=self.name,
            description=self.description,
            api_key=api_key,
            verbose=verbose,
            model_name=model_name,
            temperature=temperature,
            base_url=base_url
        )

        # Initialize specialized tools from registry
        self.tools: Dict[str, BaseTool] = {}
        self._init_tools()

        self.memory = ShortTermMemory(capacity=20)

        if self.verbose:
            print(f"Initialized {self.name} agent")

    def _init_tools(self) -> None:
        """Initialize tools from the tool registry."""
        # Get search tools from registry
        web_search = _tool_registry.get_tool("web_search")
        if web_search:
            self.tools["web_search"] = web_search

        ddg_search = _tool_registry.get_tool("duckduckgo_search")
        if ddg_search:
            self.tools["duckduckgo_search"] = ddg_search

        file_ops = _tool_registry.get_tool("file_ops")
        if file_ops:
            self.tools["file_ops"] = file_ops

    def _get_search_tool(self) -> Optional[BaseTool]:
        """Get the best available search tool."""
        if "web_search" in self.tools:
            return self.tools["web_search"]
        if "duckduckgo_search" in self.tools:
            return self.tools["duckduckgo_search"]
        return None

    def research(self, topic: str, depth: str = "standard") -> ResearchResult:
        """Conduct research on a topic."""
        self._log(f"Starting research on: {topic}")

        search_tool = self._get_search_tool()
        if not search_tool:
            self._log("No search tool available")
            return ResearchResult(
                query=topic,
                findings=[],
                sources=[],
                summary="Error: No search tool available. Please install duckduckgo-search.",
                confidence=0.0
            )

        # Perform search
        search_result = search_tool.execute(query=topic)

        findings = []
        sources = []

        if search_result.success:
            results = search_result.content.get("results", [])
            for result in results[:5]:  # Top 5 results
                findings.append({
                    "title": result.get("title", ""),
                    "content": result.get("snippet", "")[:500] if result.get("snippet") else "",
                    "url": result.get("url", "")
                })
                sources.append(result.get("url", ""))

        # Create summary
        summary_prompt = f"""
        Summarize the following research findings on: {topic}

        Findings:
        {chr(10).join([f"- {f['title']}: {f['content'][:200]}" for f in findings])}

        Provide a concise summary of the key information.
        """

        summary = self._call_llm(summary_prompt)

        result = ResearchResult(
            query=topic,
            findings=findings,
            sources=sources,
            summary=summary,
            confidence=0.8 if findings else 0.3
        )

        # Store in memory
        self.memory.add_message(
            "user",
            f"Research topic: {topic}"
        )
        self.memory.add_message(
            "assistant",
            f"Research complete. Summary: {summary[:200]}..."
        )

        self._log("Research complete")
        return result

    def compare(self, topics: List[str]) -> ResearchResult:
        """Compare multiple topics."""
        self._log(f"Comparing topics: {topics}")

        results = []
        for topic in topics:
            result = self.research(topic)
            results.append({
                "topic": topic,
                "summary": result.summary,
                "findings": result.findings
            })

        # Create comparison summary
        comparison = self._call_llm(f"""
        Compare and contrast the following topics:

        {chr(10).join([f'- {r["topic"]}: {r["summary"]}' for r in results])}

        Provide a comparative analysis.
        """)

        return ResearchResult(
            query="Comparison: " + ", ".join(topics),
            findings=results,
            sources=[],
            summary=comparison,
            confidence=0.7
        )

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze a document file."""
        file_tool = self.tools.get("file_ops")
        if not file_tool:
            return {"error": "File operations tool not available"}

        # Read the file
        read_result = file_tool.execute(operation="read", path=file_path)

        if not read_result.success:
            return {"error": read_result.error}

        content = read_result.content.get("content", "")

        # Analyze the content
        analysis = self._call_llm(f"""
        Analyze the following document:

        {content[:2000]}

        Provide:
        1. Summary of key points
        2. Main topics discussed
        3. Key takeaways
        """)

        return {
            "path": file_path,
            "content_preview": content[:500],
            "analysis": analysis,
            "word_count": len(content.split())
        }

    def execute_task(self, message) -> str:
        """Execute a task from a message (AgentRegistry compatibility)."""
        return self.research(message.task).summary
