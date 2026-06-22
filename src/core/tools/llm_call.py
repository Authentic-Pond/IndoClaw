"""
LLM call tool for IndoClaw.
Uses LangChain to make LLM calls.
"""

from typing import Dict, List, Optional
import os

try:
    from langchain_openai import ChatOpenAI
    try:
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from .base import BaseTool, ToolResult


class LLMCallTool(BaseTool):
    """LLM call tool using LangChain."""
    
    name: str = "llm_call"
    description: str = "Make LLM calls using LangChain"
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ):
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required for LLMCallTool")
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=api_key
        )
    
    def execute(self, prompt: str, messages: List[Dict[str, str]] = None, **kwargs) -> ToolResult:
        """Execute an LLM call."""
        try:
            # If messages provided, use them; otherwise use prompt
            if messages:
                langchain_messages = self._convert_messages(messages)
            else:
                langchain_messages = [HumanMessage(content=prompt)]
            
            response = self.llm.invoke(langchain_messages, **kwargs)
            
            return ToolResult(
                success=True,
                content={
                    "response": response.content,
                    "model": self.model_name,
                    "messages_used": len(messages) if messages else 1
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List:
        """Convert message dict to LangChain message objects."""
        langchain_messages = []
        
        for msg in messages:
            role = msg.get("role", "").lower()
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages
    
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """Quick chat helper method."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        
        result = self.execute("", messages=messages)
        if result.success:
            return result.content.get("response", "")
        return result.error


# Example usage
if __name__ == "__main__":
    try:
        tool = LLMCallTool()
        print(tool.get_info())
        # print(tool.execute("What is 2+2?"))
    except Exception as e:
        print(f"Tool initialization error (API key may be missing): {e}")