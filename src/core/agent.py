"""
Core agent system for IndoClaw.
Implements the perception-reasoning-action loop.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    try:
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from .memory.short_term import ShortTermMemory
from .memory.long_term import LongTermMemory, long_term_memory
from .tools.base import BaseTool, ToolResult
from .tools.web_search import WebSearchTool
from .tools.file_ops import FileOperationTool
from .tools.calculation import CalculatorTool
from ..config.settings import settings


@dataclass
class AgentState:
    """State of the agent during execution."""
    input: str = ""
    current_task: str = ""
    plan: List[Dict[str, str]] = field(default_factory=list)
    thought: str = ""
    action: str = ""
    action_input: str = ""
    observation: str = ""
    intermediate_steps: List[Dict[str, str]] = field(default_factory=list)
    memory_context: List[Dict[str, str]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"  # pending, thinking, acting, completing


@dataclass
class AgentOutput:
    """Output from agent execution."""
    response: str
    state: AgentState
    steps: List[Dict[str, Any]]
    final_memory: List[Dict[str, str]] = field(default_factory=list)


class IndoClawAgent:
    """
    Core agent for IndoClaw AI OS.
    Implements the perception-reasoning-action loop with memory.
    """
    
    def __init__(
        self,
        tools: List[BaseTool] = None,
        system_prompt: str = None,
        max_iterations: int = 10,
        verbose: bool = False
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required for IndoClawAgent")
        
        self.name = settings.agent.name
        self.role = settings.agent.role
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Initialize components
        # Check if Ollama is enabled
        if settings.llm.ollama_enabled:
            api_key = settings.llm.api_key or "not-needed-for-ollama"
            self.llm = ChatOpenAI(
                model_name=settings.llm.model_name,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
                openai_api_key=api_key,
                base_url=settings.llm.base_url
            )
            self.using_ollama = True
            if self.verbose:
                print(f"Using Ollama at {settings.llm.base_url}")
        else:
            if not settings.llm.api_key:
                raise ValueError("OPENAI_API_KEY is required when OLLAMA_ENABLED=false")
            self.llm = ChatOpenAI(
                model_name=settings.llm.model_name,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
                openai_api_key=settings.llm.api_key,
                base_url=settings.llm.api_base
            )
            self.using_ollama = False
        
        # Initialize tools
        self.tools = tools or self._default_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Initialize memory
        self.short_term_memory = ShortTermMemory(settings.memory.short_term_capacity)
        self.long_term_memory = long_term_memory
        
        # Set up prompts
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        # State tracking
        self.state = AgentState()
        self.history: List[AgentState] = []
        
        if self.verbose:
            print(f"Initialized {self.name} agent")
    
    def _default_tools(self) -> List[BaseTool]:
        """Create default tools for the agent."""
        return [
            WebSearchTool(
                api_key=settings.tool.tavily_api_key,
                max_results=settings.tool.max_web_search_results
            ),
            FileOperationTool(),
            CalculatorTool(),
        ]
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for the agent."""
        tools_list = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])
        
        return f"""You are {self.name}, an autonomous AI assistant designed to help users complete tasks.

Role: {self.role}

Tools available:
{tools_list}

Your workflow:
1. PERCEPTION: Understand the user's request
2. REASONING: Plan how to accomplish the task
3. ACTION: Use appropriate tools
4. OBSERVATION: Analyze results
5. ITERATE: Repeat until task is complete

Rules:
- Use tools when you need external information or to perform actions
- Be concise but thorough in your reasoning
- If a tool fails, try a different approach
- Complete tasks step by step
- Remember important information in memory

Respond in this format:
THOUGHT: Your reasoning
ACTION: The tool name to use
ACTION_INPUT: The input for the tool

When task is complete, respond with FINAL_ANSWER: Your final response"""
    
    def _log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{self.name}] {message}")
    
    def _get_memory_context(self, query: str) -> List[Dict[str, str]]:
        """Get relevant context from memory."""
        context = []
        
        # Add recent conversation history
        context.extend(self.short_term_memory.get_context())
        
        # Add relevant long-term memories
        memories = self.long_term_memory.query(query, top_k=settings.memory.long_term_top_k)
        for memory in memories:
            context.append({
                "role": "system",
                "content": f"Relevant past knowledge: {memory.content}"
            })
        
        return context
    
    def _think(self, input_text: str) -> AgentState:
        """Perform reasoning step."""
        self._log("Thinking...")
        
        # Get memory context
        memory_context = self._get_memory_context(input_text)
        
        # Build prompt
        prompt = f"""{self.system_prompt}

Current task: {input_text}

Memory context:
{chr(10).join([f'- {msg["role"]}: {msg["content"][:200]}...' for msg in memory_context])}

Begin your thinking process:"""
        
        # Get LLM response
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        thought = response.content.strip()
        
        # Extract action if present
        action = ""
        action_input = ""
        
        if "ACTION:" in thought:
            parts = thought.split("ACTION:")
            thought = parts[0].strip()
            if "ACTION_INPUT:" in parts[1]:
                action_parts = parts[1].split("ACTION_INPUT:")
                action = action_parts[0].strip()
                action_input = action_parts[1].strip()
            else:
                action = parts[1].strip()
        
        state = AgentState(
            input=input_text,
            thought=thought,
            action=action,
            action_input=action_input,
            memory_context=memory_context
        )
        
        self.state = state
        return state
    
    def _act(self, state: AgentState) -> ToolResult:
        """Perform action using selected tool."""
        self._log(f"Acting with: {state.action}")
        
        if not state.action:
            return ToolResult(
                success=True,
                content={"response": state.thought}
            )
        
        tool = self.tool_map.get(state.action)
        
        if not tool:
            return ToolResult(
                success=False,
                error=f"Unknown tool: {state.action}"
            )
        
        if not tool.is_enabled():
            return ToolResult(
                success=False,
                error=f"Tool disabled: {state.action}"
            )
        
        try:
            result = tool.execute(state.action_input)
            
            # Update long-term memory
            if result.success:
                self.long_term_memory.add(
                    f"Task: {state.input}\nAction: {state.action}\nResult: {result.content}",
                    {"type": "success", "timestamp": state.timestamp}
                )
            
            return result
        
        except Exception as e:
            self.long_term_memory.add(
                f"Task: {state.input}\nAction: {state.action}\nError: {str(e)}",
                {"type": "error", "timestamp": state.timestamp}
            )
            return ToolResult(success=False, error=str(e))
    
    def _update_memory(self, state: AgentState, result: ToolResult) -> None:
        """Update short-term memory with the interaction."""
        # Add user input
        self.short_term_memory.add_message(
            "user",
            state.input,
            timestamp=state.timestamp
        )
        
        # Add agent thought/action
        thought = f"THOUGHT: {state.thought}"
        if state.action:
            thought += f"\nACTION: {state.action}"
            thought += f"\nACTION_INPUT: {state.action_input}"
            if result.success:
                thought += f"\nOBSERVATION: {result.content}"
            else:
                thought += f"\nERROR: {result.error}"
        
        self.short_term_memory.add_message(
            "assistant",
            thought,
            timestamp=state.timestamp
        )
    
    def run(self, input_text: str) -> AgentOutput:
        """Run the agent with given input."""
        self._log(f"Starting execution for: {input_text}")
        
        steps = []
        state = self.state
        
        for iteration in range(self.max_iterations):
            # Perceive and reason
            state = self._think(input_text)
            self._update_memory(state, ToolResult(success=False))  # Pre-update
            
            # Check if we have a final answer
            if "FINAL_ANSWER:" in state.thought:
                response = state.thought.split("FINAL_ANSWER:")[1].strip()
                return AgentOutput(
                    response=response,
                    state=state,
                    steps=steps
                )
            
            # Perform action
            result = self._act(state)
            
            # Update memory with result
            self._update_memory(state, result)
            
            # Record step
            steps.append({
                "iteration": iteration + 1,
                "thought": state.thought,
                "action": state.action,
                "result": result.content if result.success else result.error,
                "timestamp": state.timestamp
            })
            
            # If no action needed, we're done
            if not state.action:
                return AgentOutput(
                    response=state.thought,
                    state=state,
                    steps=steps
                )
            
            # If result has response, we might be done
            if result.success and isinstance(result.content, dict) and "response" in result.content:
                return AgentOutput(
                    response=result.content["response"],
                    state=state,
                    steps=steps
                )
        
        # Max iterations reached
        return AgentOutput(
            response="I was unable to complete the task within the maximum number of iterations.",
            state=state,
            steps=steps
        )
    
    def clear_memory(self) -> None:
        """Clear agent's memory."""
        self.short_term_memory.clear()
        self._log("Memory cleared")


# Convenience function to create agent
def create_agent(
    tools: List[BaseTool] = None,
    verbose: bool = False
) -> IndoClawAgent:
    """Create an IndoClaw agent with default configuration."""
    return IndoClawAgent(
        tools=tools,
        verbose=verbose
    )


# Example usage
if __name__ == "__main__":
    try:
        agent = create_agent(verbose=True)
        
        # Test with a simple calculation
        result = agent.run("What is 15 * 7?")
        print(f"Result: {result.response}")
        
        # Test with a question
        result = agent.run("What is the capital of France?")
        print(f"Result: {result.response}")
        
    except Exception as e:
        print(f"Agent initialization error (API key may be missing): {e}")