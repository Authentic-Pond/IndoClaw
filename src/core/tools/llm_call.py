"""
LLM call tool for IndoClaw.
Uses the LLMFactory to get the appropriate adapter.
"""

from typing import Dict, List, Optional
import os

from ..llm_factory import LLMFactory
from .base import BaseTool, ToolResult

try:
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class LLMCallTool(BaseTool):
    """LLM call tool using the LLM adapter."""

    name: str = "llm_call"
    description: str = "Make LLM calls using the configured adapter"

    def __init__(self, **kwargs):
        super().__init__()
        self._adapter = None

    @property
    def adapter(self):
        """Lazy initialization of the adapter."""
        if self._adapter is None:
            self._adapter = LLMFactory.get_adapter()
        return self._adapter

    def _run(self, prompt: str = None, messages: List[Dict[str, str]] = None, **kwargs) -> ToolResult:
        """Execute an LLM call."""
        try:
            if messages:
                # The adapter expects a list of message dicts
                chat_messages = messages
            elif prompt:
                chat_messages = [{"role": "user", "content": prompt}]
            else:
                return ToolResult(
                    success=False,
                    error="Either 'prompt' or 'messages' must be provided"
                )

            response = self.adapter.chat(chat_messages)

            return ToolResult(
                success=True,
                content={
                    "response": response,
                    "model": getattr(self.adapter, 'model_name', 'unknown'),
                    "messages_used": len(chat_messages)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """Quick chat helper method."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        result = self.execute(messages=messages)
        if result.success:
            return result.content.get("response", "")
        return result.error
