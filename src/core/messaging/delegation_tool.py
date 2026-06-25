"""
Delegation tool for IndoClaw multi-agent system.
Allows Agent A to "send" a message to Agent B and wait for a structured response.
"""

from typing import Dict, List, Optional
from .agent_message import AgentMessage, AgentMessagePriority
from .agent_registry import get_agent_registry
from ..tools.base import BaseTool, ToolResult


class DelegationTool(BaseTool):
    """
    A tool that allows an agent to delegate tasks to other agents.

    Usage:
        delegation_tool.execute(
            receiver="researcher",
            task="Research the latest developments in quantum computing",
            context={"user_query": "Quantum computing applications"}
        )
    """

    name: str = "delegate_task"
    description: str = (
        "Delegate a task to another agent and wait for the response. "
        "Use this when another agent has specialized capabilities for the task."
    )

    def __init__(self, sender_name: str = "default_agent", **kwargs):
        """
        Initialize the delegation tool.

        Args:
            sender_name: The name/ID of the sending agent.
            **kwargs: Additional configuration.
        """
        super().__init__(**kwargs)
        self.sender_name = sender_name
        self._registry = get_agent_registry()

    def _run(self, receiver: str, task: str, **kwargs) -> ToolResult:
        """
        Execute task delegation.

        Args:
            receiver: The name of the agent to delegate to.
            task: The task to perform.
            **kwargs: Additional parameters:
                - context: Dict of context information
                - expected_output: Description of expected output
                - priority: Message priority (low, normal, high, urgent)

        Returns:
            ToolResult with the delegate's response.
        """
        # Check if receiver agent exists
        agent_info = self._registry.get_agent_info(receiver)
        if agent_info is None:
            return ToolResult(
                success=False,
                error=f"Agent '{receiver}' not found in registry. "
                      f"Available agents: {list(self._registry.list_agents().keys())}"
            )

        if not agent_info.enabled:
            return ToolResult(
                success=False,
                error=f"Agent '{receiver}' is disabled"
            )

        # Extract parameters
        context = kwargs.get("context", {})
        expected_output = kwargs.get("expected_output")
        priority_str = kwargs.get("priority", "normal")

        try:
            priority = AgentMessagePriority(priority_str)
        except ValueError:
            priority = AgentMessagePriority.NORMAL

        # Create the message
        message = AgentMessage(
            sender=self.sender_name,
            receiver=receiver,
            task=task,
            context=context,
            expected_output=expected_output,
            priority=priority,
        )

        # Get the agent instance and execute the task
        agent = self._registry.get_agent(receiver)
        if agent is None:
            return ToolResult(
                success=False,
                error=f"Agent '{receiver}' has no executor implementation"
            )

        try:
            # Execute the task through the agent
            response = agent.execute_task(message)

            return ToolResult(
                success=True,
                content={
                    "receiver": receiver,
                    "response": response,
                    "message_id": message.message_id,
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Task delegation to '{receiver}' failed: {str(e)}"
            )

    def delegate(
        self,
        receiver: str,
        task: str,
        context: Dict[str, str] = None,
        expected_output: str = None,
        priority: str = "normal",
    ) -> str:
        """
        Quick delegation helper method.

        Args:
            receiver: The name of the agent to delegate to.
            task: The task to perform.
            context: Optional context dictionary.
            expected_output: Optional description of expected output.
            priority: Message priority.

        Returns:
            The response from the delegate agent.
        """
        result = self.execute(
            receiver=receiver,
            task=task,
            context=context or {},
            expected_output=expected_output,
            priority=priority,
        )

        if result.success:
            return result.content.get("response", "")
        raise RuntimeError(f"Delegation failed: {result.error}")
