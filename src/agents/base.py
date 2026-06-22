"""
Base class for all IndoClaw agents.
"""

from typing import List, Dict, Any, Optional

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


class BaseAgent:
    """
    Base class for all IndoClaw agents.
    Provides common functionality for all agent types.
    Supports both OpenAI and Ollama models.
    """
    
    name: str = "BaseAgent"
    description: str = "Base agent class"
    
    def __init__(
        self,
        name: str = None,
        description: str = None,
        api_key: Optional[str] = None,
        verbose: bool = False,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        base_url: str = None
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required")
        
        self.name = name or self.name
        self.description = description or self.description
        self.api_key = api_key
        self.verbose = verbose
        self.model_name = model_name
        self.temperature = temperature
        self.base_url = base_url
        
        # Initialize LLM
        if base_url:
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key or "not-needed",
                base_url=base_url
            )
        else:
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key
            )
        
        self.tools: Dict[str, Any] = {}
        self.using_ollama = base_url is not None
    
    def _log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{self.name}] {message}")
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make an LLM call."""
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        response = self.llm.invoke(messages)
        return response.content.strip()
    
    def run(self, task: str, **kwargs) -> Any:
        """Run the agent with a task."""
        self._log(f"Running task: {task}")
        
        if task.lower().startswith("write "):
            return self.write(task[6:])
        elif task.lower().startswith("research "):
            return self.research(task[9:])
        else:
            return self._call_llm(task)
    
    def write(self, topic: str, **kwargs) -> Any:
        """Write content on a topic."""
        raise NotImplementedError
    
    def research(self, topic: str, **kwargs) -> Any:
        """Research a topic."""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, str]:
        """Get agent information."""
        return {
            "name": self.name,
            "description": self.description,
            "tools": list(self.tools.keys()),
            "model": self.model_name,
            "using_ollama": str(self.using_ollama)
        }


# Example usage
if __name__ == "__main__":
    agent = BaseAgent(verbose=True)
    print(agent.get_info())