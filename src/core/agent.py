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

# Import event system (optional, for Phase 5)
try:
    from .events.publisher import EventPublisher, EventType
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False

# Import approval system (optional, for Phase 5)
try:
    from .approval.base import ApprovalProvider
    APPROVAL_AVAILABLE = True
except ImportError:
    APPROVAL_AVAILABLE = False
from .tools.web_search import WebSearchTool
from .tools.file_ops import FileOperationTool
from .tools.calculation import CalculatorTool
from ..config.settings import settings
from .workspace import create_workspace_loader


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
        
        # Initialize memory - use absolute path based on project directory
        import os
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        storage_path = os.path.join(project_dir, "data", "short_term_memory.json")
        self.short_term_memory = ShortTermMemory(
            settings.memory.short_term_capacity,
            storage_path=storage_path
        )
        self.long_term_memory = long_term_memory
        
        # Initialize workspace loader and ensure workspaces exist
        from .workspace import ensure_workspaces_exists, get_agent_config, ensure_agent_workspace, create_workspace_loader
        
        # Ensure agent workspace exists (creates agent-specific folder)
        ensure_agent_workspace(self.name)
        
        # Load agent config from agent-specific workspace
        self.agent_config = get_agent_config(agent_name=self.name).load()
        
        # Create workspace loader with agent-specific workspace
        self.workspace_loader = create_workspace_loader(agent_name=self.name)
        self.agent_workspace = self.workspace_loader.load_agent_files(self.name)
        
        # Update agent name from config (in case it was overridden)
        self.name = self.agent_config.get("agent_name", self.name)
        
        # Set up prompts
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        # Inject workspace content into system prompt
        if self.agent_workspace:
            self._inject_workspace_into_prompt()
        
        # State tracking
        self.state = AgentState()
        self.history: List[AgentState] = []

        # Phase 5: Initialize event publisher and approval provider
        self._event_publisher = None
        self._approval_provider = None

        if EVENTS_AVAILABLE:
            self._event_publisher = EventPublisher()

        if APPROVAL_AVAILABLE:
            from ..approval.auto_approval import AutoApprovalProvider
            self._approval_provider = AutoApprovalProvider()
            # Configure tools with approval provider
            for tool in self.tools:
                tool.set_approval_provider(self._approval_provider)

        if self.verbose:
            print(f"Initialized {self.name} agent")
    
    def _inject_workspace_into_prompt(self) -> None:
        """
        Inject workspace file contents into the system prompt.
        Adds agent identity, rules, and behavior guidelines from workspace files.
        """
        workspace_content = []
        
        # Add SOUL.md - core identity and mission
        if "SOUL.md" in self.agent_workspace:
            workspace_content.append("\n# Agent Soul & Mission")
            workspace_content.append(self.agent_workspace["SOUL.md"])
        
        # Add IDENTITY.md - persona and tone
        if "IDENTITY.md" in self.agent_workspace:
            workspace_content.append("\n# Agent Identity")
            workspace_content.append(self.agent_workspace["IDENTITY.md"])
        
        # Add USER.md - user interaction guidelines
        if "USER.md" in self.agent_workspace:
            workspace_content.append("\n# User Interaction Guidelines")
            workspace_content.append(self.agent_workspace["USER.md"])
        
        # Add MEMORY.md - memory configuration
        if "MEMORY.md" in self.agent_workspace:
            workspace_content.append("\n# Memory Configuration")
            workspace_content.append(self.agent_workspace["MEMORY.md"])
        
        # Add TOOLS.md - tool specifications
        if "TOOLS.md" in self.agent_workspace:
            workspace_content.append("\n# Available Tools & Capabilities")
            workspace_content.append(self.agent_workspace["TOOLS.md"])
        
        # Add HEARTBEAT.md - status information
        if "HEARTBEAT.md" in self.agent_workspace:
            workspace_content.append("\n# System Status")
            workspace_content.append(self.agent_workspace["HEARTBEAT.md"])
        
        # Append workspace content to system prompt
        if workspace_content:
            self.system_prompt = self.system_prompt + "\n\n" + "\n".join(workspace_content)
            if self.verbose:
                print(f"Loaded {len(self.agent_workspace)} workspace files for {self.name}")
    
    def _default_tools(self) -> List[BaseTool]:
        """Create default tools for the agent."""
        from .tools.duckduckgo_search import DuckDuckGoSearchTool
        return [
            DuckDuckGoSearchTool(
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
    
    def _show_thinking(self, thought: str) -> None:
        """Display thinking output if enabled in settings."""
        if settings.tool.show_thinking:
            print(f"\n[THOUGHT]\n{thought}\n")
    
    def _show_tool_calling(self, action: str, action_input: str, result: ToolResult = None) -> None:
        """Display tool calling output if enabled in settings."""
        if settings.tool.show_tool_calling:
            if action:
                print(f"\n[TOOL CALLING]")
                print(f"Tool: {action}")
                print(f"Input: {action_input}")
                if result:
                    if result.success:
                        print(f"Status: Success")
                        print(f"Output: {result.content}")
                    else:
                        print(f"Status: Failed")
                        print(f"Error: {result.error}")
                print()
    
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
        
        # Build messages with proper format for LangChain
        messages = []
        
        # Add system prompt
        messages.append(SystemMessage(content=self.system_prompt))
        
        # Add memory context as messages
        for msg in memory_context:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            else:
                messages.append(SystemMessage(content=f"System: {content}"))
        
        # Add current task
        messages.append(HumanMessage(content=f"Current task: {input_text}\n\nPlease think about this task and provide your response."))
        
        # Get LLM response
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
        
        # Show tool calling output before execution
        self._show_tool_calling(state.action, state.action_input)

        # Phase 5: Publish event before tool execution
        if self._event_publisher:
            self._event_publisher.publish(
                event_type=EventType.TOOL_EXECUTED,
                agent_id=self.name,
                payload={
                    "tool": state.action,
                    "input": state.action_input
                }
            )

        try:
            result = tool.execute(state.action_input)

            # Phase 5: Publish event after tool execution
            if self._event_publisher:
                event_type = EventType.TOOL_EXECUTED
                if not result.success:
                    event_type = EventType.ERROR
                self._event_publisher.publish(
                    event_type=event_type,
                    agent_id=self.name,
                    payload={
                        "tool": state.action,
                        "input": state.action_input,
                        "success": result.success,
                        "output": result.content if result.success else result.error
                    }
                )

            # Show tool calling output after execution (with result)
            self._show_tool_calling(state.action, state.action_input, result)
            
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

        # Phase 5: Publish task start event
        if self._event_publisher:
            self._event_publisher.publish(
                event_type=EventType.TASK_START,
                agent_id=self.name,
                payload={
                    "task": input_text
                }
            )
        
        steps = []
        state = self.state
        
        for iteration in range(self.max_iterations):
            # Perceive and reason
            state = self._think(input_text)
            
            # Show thinking output if enabled
            self._show_thinking(state.thought)
            
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
                # Phase 5: Publish task end event
                if self._event_publisher:
                    self._event_publisher.publish(
                        event_type=EventType.TASK_END,
                        agent_id=self.name,
                        payload={
                            "status": "completed_no_action",
                            "response": state.thought
                        }
                    )
                return AgentOutput(
                    response=state.thought,
                    state=state,
                    steps=steps
                )

            # If result has response, we might be done
            if result.success and isinstance(result.content, dict) and "response" in result.content:
                # Phase 5: Publish task end event
                if self._event_publisher:
                    self._event_publisher.publish(
                        event_type=EventType.TASK_END,
                        agent_id=self.name,
                        payload={
                            "status": "completed_with_response",
                            "response": result.content["response"]
                        }
                    )
                return AgentOutput(
                    response=result.content["response"],
                    state=state,
                    steps=steps
                )

        # Max iterations reached
        # Phase 5: Publish task end event with error
        if self._event_publisher:
            self._event_publisher.publish(
                event_type=EventType.TASK_END,
                agent_id=self.name,
                payload={
                    "status": "max_iterations_reached"
                }
            )
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