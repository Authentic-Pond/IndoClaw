"""
Tests for multi-agent messaging module (Phase 3).
"""

import pytest
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.messaging.agent_message import AgentMessage, AgentMessagePriority
from src.core.messaging.agent_registry import AgentRegistry, AgentInfo, get_agent_registry
from src.core.tools.base import ToolResult


class TestAgentMessage:
    """Tests for AgentMessage."""

    def test_create_message(self):
        """Test creating a basic message."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Perform a search",
        )

        assert message.sender == "agent_a"
        assert message.receiver == "agent_b"
        assert message.task == "Perform a search"
        assert message.priority == AgentMessagePriority.NORMAL
        assert message.context == {}

    def test_message_with_priority(self):
        """Test message with priority."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Urgent task",
            priority=AgentMessagePriority.URGENT,
        )

        assert message.priority == AgentMessagePriority.URGENT

    def test_message_with_context(self):
        """Test message with context."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Task with context",
            context={"key1": "value1", "key2": "value2"},
        )

        assert message.context["key1"] == "value1"
        assert message.context["key2"] == "value2"

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Test task",
        )

        data = message.to_dict()

        assert data["sender"] == "agent_a"
        assert data["receiver"] == "agent_b"
        assert data["task"] == "Test task"
        assert "message_id" in data
        assert "timestamp" in data
        assert data["priority"] == "normal"

    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        original = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Test task",
            priority=AgentMessagePriority.HIGH,
            context={"key": "value"},
        )

        data = original.to_dict()
        restored = AgentMessage.from_dict(data)

        assert restored.sender == original.sender
        assert restored.receiver == original.receiver
        assert restored.task == original.task
        assert restored.priority == original.priority
        assert restored.context == original.context

    def test_priority_chaining(self):
        """Test priority setter chaining."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Test",
        ).set_priority(AgentMessagePriority.HIGH)

        assert message.priority == AgentMessagePriority.HIGH

    def test_context_chaining(self):
        """Test context setter chaining."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Test",
        ).add_context("key1", "value1").add_context("key2", "value2")

        assert message.context["key1"] == "value1"
        assert message.context["key2"] == "value2"

    def test_metadata_chaining(self):
        """Test metadata setter chaining."""
        message = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            task="Test",
        ).add_metadata("trace_id", "12345")

        assert message.metadata["trace_id"] == "12345"


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_register_agent(self):
        """Test registering an agent."""
        registry = AgentRegistry()

        registry.register(
            name="researcher",
            description="Research specialist agent",
            role="Researcher",
            capabilities={"search": "Web search capability", "analyze": "Data analysis capability"},
        )

        info = registry.get_agent_info("researcher")
        assert info is not None
        assert info.name == "researcher"
        assert info.description == "Research specialist agent"

    def test_register_agent_with_factory(self):
        """Test registering an agent with factory."""
        registry = AgentRegistry()

        class MockAgent:
            def __init__(self):
                self.name = "mock"

        registry.register(
            name="mock_agent",
            description="Mock agent",
            role="Helper",
            capabilities={},
            factory=lambda: MockAgent(),
        )

        agent = registry.get_agent("mock_agent")
        assert agent is not None
        assert agent.name == "mock"

    def test_unregister_agent(self):
        """Test unregistering an agent."""
        registry = AgentRegistry()

        registry.register(
            name="test_agent",
            description="Test agent",
            role="Test",
            capabilities={},
        )

        assert registry.get_agent_info("test_agent") is not None

        registry.unregister("test_agent")
        assert registry.get_agent_info("test_agent") is None

    def test_enable_disable_agent(self):
        """Test enabling/disabling an agent."""
        registry = AgentRegistry()

        registry.register(
            name="test_agent",
            description="Test agent",
            role="Test",
            capabilities={},
        )

        info = registry.get_agent_info("test_agent")
        assert info.enabled is True

        registry.disable_agent("test_agent")
        info = registry.get_agent_info("test_agent")
        assert info.enabled is False

        registry.enable_agent("test_agent")
        info = registry.get_agent_info("test_agent")
        assert info.enabled is True

    def test_list_agents(self):
        """Test listing all agents."""
        registry = AgentRegistry()

        registry.register(
            name="agent1",
            description="First agent",
            role="Helper",
            capabilities={},
        )

        registry.register(
            name="agent2",
            description="Second agent",
            role="Helper",
            capabilities={},
        )

        agents = registry.list_agents()
        assert "agent1" in agents
        assert "agent2" in agents
        assert agents["agent1"]["description"] == "First agent"

    def test_get_enabled_agents(self):
        """Test getting only enabled agents."""
        registry = AgentRegistry()

        registry.register(
            name="enabled_agent",
            description="Enabled agent",
            role="Helper",
            capabilities={},
        )

        registry.register(
            name="disabled_agent",
            description="Disabled agent",
            role="Helper",
            capabilities={},
        )
        registry.disable_agent("disabled_agent")

        enabled = registry.get_enabled_agents()
        assert "enabled_agent" in enabled
        assert "disabled_agent" not in enabled

    def test_create_agent(self):
        """Test creating an agent with configuration."""
        registry = AgentRegistry()

        class ConfigurableAgent:
            def __init__(self, config_value=None):
                self.config_value = config_value

        registry.register(
            name="config_agent",
            description="Configurable agent",
            role="Helper",
            capabilities={},
            factory=lambda **kwargs: ConfigurableAgent(**kwargs),
        )

        agent = registry.create_agent("config_agent", config_value="test")
        assert agent is not None
        assert agent.config_value == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
