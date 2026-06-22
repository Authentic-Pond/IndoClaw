"""
Researcher Agent for IndoClaw.
Specialized in gathering and analyzing information from various sources.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from langchain_openai import ChatOpenAI
    try:
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage, AIMessage
    try:
        from langchain_core.prompts import PromptTemplate
    except ImportError:
        from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from .base import BaseAgent
from ..core.tools.web_search import WebSearchTool
from ..core.tools.file_ops import FileOperationTool
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
    Supports both OpenAI and Ollama models.
    """
    
    name: str = "Researcher"
    description: str = "Specializes in gathering and analyzing information"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        verbose: bool = False
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required")
        
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
        
        # Initialize specialized tools
        self.tools = {
            "web_search": WebSearchTool(api_key=self._get_api_key()),
            "file_ops": FileOperationTool()
        }
        
        self.memory = ShortTermMemory(capacity=20)
        
        if self.verbose:
            print(f"Initialized {self.name} agent")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from parameter or environment."""
        return self.api_key
    
    def research(self, topic: str, depth: str = "standard") -> ResearchResult:
        """Conduct research on a topic."""
        self._log(f"Starting research on: {topic}")
        
        # Get initial information
        web_search = self.tools["web_search"]
        search_result = web_search.execute(topic)
        
        findings = []
        sources = []
        
        if search_result.success:
            results = search_result.content.get("results", [])
            for result in results[:5]:  # Top 5 results
                findings.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:500],
                    "url": result.get("url", "")
                })
                sources.append(result.get("url", ""))
        
        # Create summary
        summary_prompt = PromptTemplate.from_template("""
        Summarize the following research findings on: {topic}

        Findings:
        {findings}

        Provide a concise summary of the key information.
        """)
        
        findings_text = "\n\n".join([
            f"- {f['title']}: {f['content']}"
            for f in findings
        ])
        
        summary = self._call_llm(
            summary_prompt.format(topic=topic, findings=findings_text)
        )
        
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
        file_tool = self.tools["file_ops"]
        
        # Read the file
        read_result = file_tool.execute("read", path=file_path)
        
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


# Example usage
if __name__ == "__main__":
    try:
        agent = ResearcherAgent(verbose=True)
        
        # Test research
        result = agent.research("Latest developments in AI")
        print(f"Summary: {result.summary}")
        
    except Exception as e:
        print(f"Agent initialization error (API key may be missing): {e}")