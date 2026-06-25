"""
Agent registry for IndoClaw multi-agent system.
Provides discovery and management of available agents.
"""

from typing import Dict, Optional, Callable
from dataclasses import dataclass
import uuid


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    name: str
    description: str
    role: str
    capabilities: Dict[str, str]
    enabled: bool = True


class AgentRegistry:
    """
    Registry for all available agents in IndoClaw.
    Allows dynamic discovery and management of agents.

    Agents can be:
    - Registered programmatically
    - Discovered via list_agents()
    - Retrieved by name via get_agent()
    """

    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}
        self._agent_factories: Dict[str, Callable[[], "BaseAgent"]] = {}

    def register(
        self,
        name: str,
        description: str,
        role: str,
        capabilities: Dict[str, str],
        factory: Optional[Callable[[], "BaseAgent"]] = None,
    ) -> None:
        """
        Register an agent type in the registry.

        Args:
            name: Unique name for the agent (e.g., "researcher", "writer")
            description: Human-readable description of the agent
            role: The primary role of the agent
            capabilities: Dictionary of capabilities (capability_name -> description)
            factory: Optional callable that creates an agent instance
        """
        agent_info = AgentInfo(
            name=name,
            description=description,
            role=role,
            capabilities=capabilities,
        )
        self._agents[name] = agent_info

        if factory is not None:
            self._agent_factories[name] = factory

    def unregister(self, name: str) -> None:
        """
        Unregister an agent by name.

        Args:
            name: The name of the agent to remove.
        """
        if name in self._agents:
            del self._agents[name]
        if name in self._agent_factories:
            del self._agent_factories[name]

    def enable_agent(self, name: str) -> None:
        """Enable a disabled agent."""
        if name in self._agents:
            self._agents[name].enabled = True

    def disable_agent(self, name: str) -> None:
        """Disable an agent."""
        if name in self._agents:
            self._agents[name].enabled = False

    def get_agent_info(self, name: str) -> Optional[AgentInfo]:
        """
        Get agent information by name.

        Args:
            name: The name of the agent.

        Returns:
            AgentInfo if found, otherwise None.
        """
        return self._agents.get(name)

    def get_agent(self, name: str) -> Optional["BaseAgent"]:
        """
        Get an agent instance by name (if factory is registered).

        Args:
            name: The name of the agent.

        Returns:
            Agent instance if factory exists, otherwise None.
        """
        if name in self._agent_factories:
            return self._agent_factories[name]()
        return None

    def list_agents(self) -> Dict[str, Dict]:
        """
        List all registered agents.

        Returns:
            Dictionary mapping agent names to their info.
        """
        return {
            name: {
                "name": info.name,
                "description": info.description,
                "role": info.role,
                "capabilities": info.capabilities,
                "enabled": info.enabled,
            }
            for name, info in self._agents.items()
        }

    def get_enabled_agents(self) -> Dict[str, Dict]:
        """Get only enabled agents."""
        return {
            name: info
            for name, info in self.list_agents().items()
            if info.get("enabled", True)
        }

    def create_agent(self, name: str, **kwargs) -> Optional["BaseAgent"]:
        """
        Create an agent instance with optional configuration.

        Args:
            name: The name of the agent to create.
            **kwargs: Additional configuration for the agent.

        Returns:
            Agent instance if registered, otherwise None.
        """
        agent = self.get_agent(name)
        if agent is not None:
            # Apply any additional configuration
            for key, value in kwargs.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
        return agent


# Global agent registry instance
_agent_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    return _agent_registry


def register_agent(
    name: str,
    description: str,
    role: str,
    capabilities: Dict[str, str],
    factory: Optional[Callable[[], "BaseAgent"]] = None,
) -> None:
    """Convenience function to register an agent to the global registry."""
    _agent_registry.register(name, description, role, capabilities, factory)
