"""
Writer Agent for IndoClaw.
Specialized in content creation and writing tasks.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .base import BaseAgent
from ..core.tools.base import BaseTool
from ..core.tools import _tool_registry
from ..core.memory.short_term import ShortTermMemory
from ..config.settings import settings


@dataclass
class WritingResult:
    """Result of a writing task."""
    title: str
    content: str
    format: str
    word_count: int
    file_path: Optional[str] = None


class WriterAgent(BaseAgent):
    """
    Writer agent specialized in content creation and writing.
    Uses the tool registry for pluggable tool access.
    """

    name: str = "Writer"
    description: str = "Specializes in content creation and writing"

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

        self.memory = ShortTermMemory(capacity=15)

        if self.verbose:
            print(f"Initialized {self.name} agent")

    def _init_tools(self) -> None:
        """Initialize tools from the tool registry."""
        file_ops = _tool_registry.get_tool("file_ops")
        if file_ops:
            self.tools["file_ops"] = file_ops

    def write(self, topic: str, format: str = "article", length: str = "medium") -> WritingResult:
        """Write content on a topic."""
        self._log(f"Writing {format} on: {topic}")

        # Determine length constraints
        length_constraints = {
            "short": {"min_words": 200, "max_words": 400},
            "medium": {"min_words": 500, "max_words": 800},
            "long": {"min_words": 1000, "max_words": 2000}
        }

        constraints = length_constraints.get(length, length_constraints["medium"])

        # Generate content
        prompt = f"""
        Write a {format} about: {topic}

        Requirements:
        - Target: {constraints["min_words"]}-{constraints["max_words"]} words
        - Format: {format}
        - Include introduction, body, and conclusion
        - Use engaging and clear language

        Provide only the content, no additional text.
        """

        content = self._call_llm(prompt)

        result = WritingResult(
            title=topic,
            content=content,
            format=format,
            word_count=len(content.split()),
            file_path=None
        )

        self._log(f"Writing complete: {result.word_count} words")
        return result

    def write_file(self, topic: str, file_path: str, format: str = "markdown") -> WritingResult:
        """Write content to a file."""
        result = self.write(topic, format=format)

        # Write to file
        file_tool = self.tools.get("file_ops")
        if file_tool:
            file_tool.execute(
                operation="write",
                path=file_path,
                content=f"# {result.title}\n\n{result.content}"
            )

        result.file_path = file_path
        return result

    def edit(self, content: str, edits: List[str]) -> str:
        """Apply edits to existing content."""
        edits_text = "\n".join([f"- {edit}" for edit in edits])

        prompt = f"""
        Apply the following edits to the content:

        Content:
        {content}

        Edits to apply:
        {edits_text}

        Return only the edited content.
        """

        return self._call_llm(prompt)

    def summarize(self, content: str, length: str = "short") -> str:
        """Summarize content."""
        length_instructions = {
            "short": "Provide a brief summary of 2-3 sentences.",
            "medium": "Provide a concise summary of 5-7 sentences.",
            "long": "Provide a comprehensive summary of 10-15 sentences."
        }

        prompt = f"""
        {length_instructions.get(length, length_instructions["short"])}

        Content:
        {content[:3000]}

        Summary:
        """

        return self._call_llm(prompt)

    def execute_task(self, message) -> str:
        """Execute a task from a message (AgentRegistry compatibility)."""
        return self.write(message.task).content
